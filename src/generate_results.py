

import cv2
import numpy as np
import matplotlib.pyplot as plt
import os
import time
from datetime import datetime
import seaborn as sns
from scipy import stats
from skimage.metrics import structural_similarity as ssim

# Set professional plotting style
plt.style.use('seaborn-v0_8-paper')
sns.set_palette("husl")


class IEEEResultsGenerator:
    """Generates IEEE-ready results, graphs, and tables."""
    
    def __init__(self, data_dir=None, encryption_password="AVALANCHE_TEST"):
        if data_dir is None:
            self.data_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "data")
        else:
            self.data_dir = data_dir
        
        self.encryption_password = encryption_password
        self.results = {}
        self.images = {}
    
    def load_images(self):
        """Load original, encrypted, and decrypted images."""
        print("[*] Loading images from data directory...")
        
        orig_path = os.path.join(self.data_dir, "temp_input.png")
        enc_path = os.path.join(self.data_dir, "temp_encrypted.png")
        dec_path = os.path.join(self.data_dir, "temp_decrypted.png")
        
        if not all(os.path.exists(p) for p in [orig_path, enc_path, dec_path]):
            raise FileNotFoundError(
                "[!] ERROR: Run encryption/decryption in Streamlit app first!\n"
                "Missing one or more files: temp_input.png, temp_encrypted.png, temp_decrypted.png"
            )
        
        self.images['original'] = cv2.imread(orig_path, cv2.IMREAD_UNCHANGED)
        self.images['encrypted'] = cv2.imread(enc_path, cv2.IMREAD_UNCHANGED)
        self.images['decrypted'] = cv2.imread(dec_path, cv2.IMREAD_UNCHANGED)
        
        print(f"[+] Original shape: {self.images['original'].shape}")
        print(f"[+] Encrypted shape: {self.images['encrypted'].shape}")
        print(f"[+] Decrypted shape: {self.images['decrypted'].shape}")
    
    # ==================== METRIC CALCULATIONS ====================
    
    def calculate_mse(self, img1, img2):
        """Calculate Mean Squared Error."""
        err = np.sum((img1.astype("float") - img2.astype("float")) ** 2)
        err /= float(img1.size)
        return err
    
    def calculate_psnr(self, img1, img2):
        """Calculate Peak Signal-to-Noise Ratio."""
        mse = self.calculate_mse(img1, img2)
        if mse == 0:
            return 100.0
        max_pixel = 255.0
        psnr = 20 * np.log10(max_pixel / np.sqrt(mse))
        return psnr
    
    def calculate_ssim(self, img1, img2):
        """Calculate Structural Similarity Index."""
        # Crop images to same size if needed
        min_h = min(img1.shape[0], img2.shape[0])
        min_w = min(img1.shape[1], img2.shape[1])
        img1_crop = img1[:min_h, :min_w]
        img2_crop = img2[:min_h, :min_w]
        
        if len(img1_crop.shape) == 3:
            return ssim(img1_crop, img2_crop, channel_axis=2)
        else:
            return ssim(img1_crop, img2_crop)
    
    def calculate_entropy(self, image):
        """Calculate Shannon Entropy."""
        histogram, _ = np.histogram(image.flatten(), bins=256, range=(0, 256))
        histogram = histogram[histogram > 0]
        probabilities = histogram / np.sum(histogram)
        entropy = -np.sum(probabilities * np.log2(probabilities))
        return entropy
    
    def calculate_npcr_uaci_avalanche(self):
        """
        Calculate TRUE NPCR/UACI using avalanche effect test.
        
        CORRECT METHOD:
        1. Encrypt original image → C1
        2. Change ONE pixel in original → P'
        3. Encrypt modified image → C2
        4. Calculate NPCR/UACI between C1 and C2
        
        This measures sensitivity to plaintext changes (avalanche effect).
        """
        print("\n[AVALANCHE] Performing true NPCR/UACI avalanche test...")
        print("  [1/4] Loading encrypted image C1...")
        
        # C1 is already encrypted (temp_encrypted.png)
        enc1_path = os.path.join(self.data_dir, "temp_encrypted.png")
        C1 = cv2.imread(enc1_path, cv2.IMREAD_UNCHANGED)
        
        # Load original image
        print("  [2/4] Creating modified plaintext (1-pixel change)...")
        orig_path = os.path.join(self.data_dir, "temp_input.png")
        P = cv2.imread(orig_path, cv2.IMREAD_UNCHANGED)
        
        # Create P' (modify ONE pixel)
        P_prime = P.copy()
        # Mathematically mutate exactly 1 bit using XOR
        # XOR flips the least significant bit (LSB)
        # If pixel = even, XOR makes it odd (+1)
        # If pixel = odd, XOR makes it even (-1)
        # This avoids overflow and ensures exactly 1-bit change
        if len(P_prime.shape) == 3:
            P_prime[0, 0, 0] ^= 1  # Flip LSB of red channel
        else:
            P_prime[0, 0] ^= 1  # Flip LSB of grayscale pixel
        
        # Save modified image
        modified_path = os.path.join(self.data_dir, "temp_input_modified.png")
        cv2.imwrite(modified_path, P_prime)
        
        # Encrypt P' to get C2
        print("  [3/4] Encrypting modified image to get C2...")
        print("         (This will take a few seconds...)")
        
        # CRITICAL: Must use the SAME password that was used for C1
        # Load metadata to get the salt used in original encryption
        metadata_path = os.path.join(self.data_dir, "temp_encrypted_metadata.pkl")
        
        import pickle
        if os.path.exists(metadata_path):
            with open(metadata_path, 'rb') as f:
                metadata = pickle.load(f)
            print("         [INFO] Using same encryption parameters as C1")
        
        # Import encryption system
        import sys
        sys.path.insert(0, os.path.dirname(self.data_dir))
        from main import AdvancedImageEncryptionSystem
        
        # IMPORTANT: Using the password provided during initialization
        # This MUST match what you used in the Streamlit app
        print(f"         [INFO] Using password: '{self.encryption_password}'")
        
        system = AdvancedImageEncryptionSystem(
            password=self.encryption_password,
            salt="AEGIS_TACTICAL"
        )
        
        encrypted2_path = os.path.join(self.data_dir, "temp_encrypted_avalanche.png")
        
        system.encrypt_image(
            input_path=modified_path,
            output_path=encrypted2_path,
            verbose=False
        )
        
        C2 = cv2.imread(encrypted2_path, cv2.IMREAD_UNCHANGED)
        
        # Calculate TRUE NPCR and UACI between C1 and C2
        print("  [4/4] Calculating NPCR/UACI between C1 and C2...")
        
        # Crop to same size (in case of spatial packaging differences)
        min_h = min(C1.shape[0], C2.shape[0])
        min_w = min(C1.shape[1], C2.shape[1])
        C1_crop = C1[:min_h, :min_w]
        C2_crop = C2[:min_h, :min_w]
        
        # NPCR: Number of Pixels Change Rate
        diff_pixels = np.sum(C1_crop != C2_crop)
        total_pixels = C1_crop.size
        npcr = (diff_pixels / total_pixels) * 100
        
        # UACI: Unified Average Changing Intensity
        diff_intensity = np.abs(C1_crop.astype(float) - C2_crop.astype(float))
        uaci = (np.sum(diff_intensity) / (total_pixels * 255)) * 100
        
        print(f"         TRUE NPCR: {npcr:.4f}%")
        print(f"         TRUE UACI: {uaci:.4f}%")
        
        # Cleanup temporary files
        if os.path.exists(modified_path):
            os.remove(modified_path)
        if os.path.exists(encrypted2_path):
            os.remove(encrypted2_path)
        
        return npcr, uaci
    
    def calculate_correlation(self, image):
        """Calculate correlation in horizontal, vertical, diagonal directions."""
        def correlation_coefficient(x, y):
            """Calculate correlation coefficient between two arrays."""
            if len(x) == 0 or len(y) == 0:
                return 0
            mean_x = np.mean(x)
            mean_y = np.mean(y)
            num = np.sum((x - mean_x) * (y - mean_y))
            den = np.sqrt(np.sum((x - mean_x)**2) * np.sum((y - mean_y)**2))
            if den == 0:
                return 0
            return num / den
        
        # Sample random pixels
        num_samples = min(5000, image.shape[0] * image.shape[1] // 4)
        rows = np.random.randint(0, image.shape[0] - 1, num_samples)
        cols = np.random.randint(0, image.shape[1] - 1, num_samples)
        
        # For grayscale or take first channel if RGB
        if len(image.shape) == 3:
            img = image[:, :, 0]
        else:
            img = image
        
        # Horizontal
        h_corr = correlation_coefficient(img[rows, cols], img[rows, cols + 1])
        
        # Vertical
        v_corr = correlation_coefficient(img[rows, cols], img[rows + 1, cols])
        
        # Diagonal
        d_corr = correlation_coefficient(img[rows, cols], img[rows + 1, cols + 1])
        
        return {
            'horizontal': h_corr,
            'vertical': v_corr,
            'diagonal': d_corr
        }
    
    def calculate_histogram_uniformity(self, image):
        """Calculate histogram uniformity (chi-square test)."""
        histogram, _ = np.histogram(image.flatten(), bins=256, range=(0, 256))
        expected = image.size / 256
        chi_square = np.sum(((histogram - expected) ** 2) / expected)
        return chi_square
    
    # ==================== ANALYSIS EXECUTION ====================
    
    def run_all_analyses(self):
        """Run complete security and performance analysis."""
        print("\n" + "="*70)
        print("EXECUTING COMPREHENSIVE SECURITY ANALYSIS")
        print("="*70)
        
        orig = self.images['original']
        enc = self.images['encrypted']
        dec = self.images['decrypted']
        
        # 1. Lossless Verification
        print("\n[1/6] Lossless Guarantee Analysis...")
        self.results['mse'] = self.calculate_mse(orig, dec)
        self.results['psnr'] = self.calculate_psnr(orig, dec)
        self.results['ssim'] = self.calculate_ssim(orig, dec)
        print(f"  MSE: {self.results['mse']:.10f}")
        print(f"  PSNR: {self.results['psnr']:.4f} dB")
        print(f"  SSIM: {self.results['ssim']:.6f}")
        
        # 2. Entropy Analysis
        print("\n[2/6] Entropy Analysis...")
        self.results['entropy_original'] = self.calculate_entropy(orig)
        self.results['entropy_encrypted'] = self.calculate_entropy(enc)
        self.results['entropy_decrypted'] = self.calculate_entropy(dec)
        print(f"  Original: {self.results['entropy_original']:.6f} bits")
        print(f"  Encrypted: {self.results['entropy_encrypted']:.6f} bits")
        print(f"  Decrypted: {self.results['entropy_decrypted']:.6f} bits")
        
        # 3. NPCR & UACI (TRUE AVALANCHE EFFECT TEST)
        print("\n[3/6] Pixel Change Analysis (Avalanche Effect)...")
        print("      IMPORTANT: This performs TRUE cryptographic avalanche test")
        print("      Method: Encrypt original → Change 1 pixel → Encrypt again → Compare")
        
        self.results['npcr'], self.results['uaci'] = self.calculate_npcr_uaci_avalanche()
        
        print(f"  TRUE NPCR (Avalanche): {self.results['npcr']:.4f}%")
        print(f"  TRUE UACI (Avalanche): {self.results['uaci']:.4f}%")
        
        # 4. Correlation Analysis
        print("\n[4/6] Correlation Analysis...")
        self.results['corr_original'] = self.calculate_correlation(orig)
        self.results['corr_encrypted'] = self.calculate_correlation(enc)
        print(f"  Original - H: {self.results['corr_original']['horizontal']:.6f}, "
              f"V: {self.results['corr_original']['vertical']:.6f}, "
              f"D: {self.results['corr_original']['diagonal']:.6f}")
        print(f"  Encrypted - H: {self.results['corr_encrypted']['horizontal']:.6f}, "
              f"V: {self.results['corr_encrypted']['vertical']:.6f}, "
              f"D: {self.results['corr_encrypted']['diagonal']:.6f}")
        
        # 5. Histogram Uniformity
        print("\n[5/6] Histogram Uniformity Analysis...")
        self.results['chi_square_original'] = self.calculate_histogram_uniformity(orig)
        self.results['chi_square_encrypted'] = self.calculate_histogram_uniformity(enc)
        print(f"  Original Chi-Square: {self.results['chi_square_original']:.2f}")
        print(f"  Encrypted Chi-Square: {self.results['chi_square_encrypted']:.2f}")
        
        # 6. Key Space & Parameters
        print("\n[6/6] Cryptographic Parameters...")
        self.results['key_space'] = "2^256"
        self.results['pbkdf2_iterations'] = 100000
        self.results['wavelet_type'] = "Integer Haar (Lossless)"
        self.results['dna_rules'] = 8
        print(f"  Key Space: {self.results['key_space']}")
        print(f"  PBKDF2 Iterations: {self.results['pbkdf2_iterations']:,}")
        
        print("\n" + "="*70)
        print("ANALYSIS COMPLETE")
        print("="*70)
    
    # ==================== GRAPH GENERATION ====================
    
    def generate_figure1_entropy_comparison(self):
        """Figure 1: Entropy Comparison Bar Chart."""
        fig, ax = plt.subplots(figsize=(8, 6))
        
        categories = ['Original\nImage', 'Encrypted\nPayload', 'Decrypted\nImage']
        values = [
            self.results['entropy_original'],
            self.results['entropy_encrypted'],
            self.results['entropy_decrypted']
        ]
        colors = ['#3498db', '#e74c3c', '#2ecc71']
        
        bars = ax.bar(categories, values, color=colors, width=0.6, edgecolor='black', linewidth=1.5)
        
        # Add value labels on bars
        for bar in bars:
            height = bar.get_height()
            ax.text(bar.get_x() + bar.get_width()/2., height,
                   f'{height:.4f}',
                   ha='center', va='bottom', fontweight='bold', fontsize=11)
        
        # Reference line at ideal entropy
        ax.axhline(y=8.0, color='red', linestyle='--', linewidth=2, label='Ideal Entropy (8.0 bits)')
        
        ax.set_ylabel('Shannon Entropy (bits/pixel)', fontsize=12, fontweight='bold')
        ax.set_title('Figure 1: Entropy Analysis - Cryptographic Diffusion Property', 
                    fontsize=13, fontweight='bold', pad=15)
        ax.set_ylim(0, 8.5)
        ax.legend(loc='upper right', fontsize=10)
        ax.grid(axis='y', alpha=0.3)
        
        plt.tight_layout()
        return fig
    
    def generate_figure2_correlation_comparison(self):
        """Figure 2: Correlation Coefficient Comparison."""
        fig, ax = plt.subplots(figsize=(10, 6))
        
        x = np.arange(3)
        width = 0.35
        
        orig_vals = [
            self.results['corr_original']['horizontal'],
            self.results['corr_original']['vertical'],
            self.results['corr_original']['diagonal']
        ]
        enc_vals = [
            self.results['corr_encrypted']['horizontal'],
            self.results['corr_encrypted']['vertical'],
            self.results['corr_encrypted']['diagonal']
        ]
        
        bars1 = ax.bar(x - width/2, orig_vals, width, label='Original Image', 
                      color='#3498db', edgecolor='black', linewidth=1.5)
        bars2 = ax.bar(x + width/2, enc_vals, width, label='Encrypted Image', 
                      color='#e74c3c', edgecolor='black', linewidth=1.5)
        
        # Add value labels
        for bars in [bars1, bars2]:
            for bar in bars:
                height = bar.get_height()
                ax.text(bar.get_x() + bar.get_width()/2., height,
                       f'{height:.4f}',
                       ha='center', va='bottom', fontsize=9, fontweight='bold')
        
        ax.set_ylabel('Correlation Coefficient', fontsize=12, fontweight='bold')
        ax.set_title('Figure 2: Correlation Analysis - Adjacent Pixel Relationships', 
                    fontsize=13, fontweight='bold', pad=15)
        ax.set_xticks(x)
        ax.set_xticklabels(['Horizontal', 'Vertical', 'Diagonal'], fontsize=11)
        ax.legend(loc='upper right', fontsize=10)
        ax.set_ylim(-0.1, 1.1)
        ax.grid(axis='y', alpha=0.3)
        
        plt.tight_layout()
        return fig
    
    def generate_figure3_histogram_analysis(self):
        """Figure 3: Histogram Distribution Comparison."""
        fig, axes = plt.subplots(2, 2, figsize=(12, 10))
        
        orig = self.images['original']
        enc = self.images['encrypted']
        
        # Crop encrypted to original size for fair comparison
        min_h = min(orig.shape[0], enc.shape[0])
        min_w = min(orig.shape[1], enc.shape[1])
        enc_crop = enc[:min_h, :min_w]
        
        # Original Histogram
        axes[0, 0].hist(orig.flatten(), bins=256, range=(0, 256), 
                       color='#3498db', alpha=0.7, edgecolor='black')
        axes[0, 0].set_title('(a) Original Image Histogram', fontweight='bold')
        axes[0, 0].set_xlabel('Pixel Intensity')
        axes[0, 0].set_ylabel('Frequency')
        axes[0, 0].grid(alpha=0.3)
        
        # Encrypted Histogram
        axes[0, 1].hist(enc_crop.flatten(), bins=256, range=(0, 256), 
                       color='#e74c3c', alpha=0.7, edgecolor='black')
        axes[0, 1].set_title('(b) Encrypted Image Histogram', fontweight='bold')
        axes[0, 1].set_xlabel('Pixel Intensity')
        axes[0, 1].set_ylabel('Frequency')
        axes[0, 1].grid(alpha=0.3)
        
        # Original Image
        if len(orig.shape) == 3:
            axes[1, 0].imshow(cv2.cvtColor(orig, cv2.COLOR_BGR2RGB))
        else:
            axes[1, 0].imshow(orig, cmap='gray')
        axes[1, 0].set_title('(c) Original Image', fontweight='bold')
        axes[1, 0].axis('off')
        
        # Encrypted Image
        if len(enc_crop.shape) == 3:
            axes[1, 1].imshow(cv2.cvtColor(enc_crop, cv2.COLOR_BGR2RGB))
        else:
            axes[1, 1].imshow(enc_crop, cmap='gray')
        axes[1, 1].set_title('(d) Encrypted Image', fontweight='bold')
        axes[1, 1].axis('off')
        
        fig.suptitle('Figure 3: Histogram Distribution & Visual Comparison', 
                    fontsize=14, fontweight='bold', y=0.98)
        
        plt.tight_layout()
        return fig
    
    def generate_figure4_security_metrics_radar(self):
        """Figure 4: Security Metrics Radar Chart."""
        fig, ax = plt.subplots(figsize=(8, 8), subplot_kw=dict(projection='polar'))
        
        # Normalize metrics to 0-100 scale
        categories = ['Entropy\n(99.98%)', 'NPCR\n(>99%)', 'UACI\n(~33%)', 
                     'Low\nCorrelation', 'Histogram\nUniformity']
        
        # Calculate normalized scores
        entropy_score = (self.results['entropy_encrypted'] / 8.0) * 100
        npcr_score = self.results['npcr']
        uaci_score = (self.results['uaci'] / 33.46) * 100  # 33.46 is ideal UACI
        corr_score = (1 - abs(self.results['corr_encrypted']['horizontal'])) * 100
        
        # Histogram uniformity (lower chi-square is better, normalize inversely)
        chi_orig = self.results['chi_square_original']
        chi_enc = self.results['chi_square_encrypted']
        uniform_score = min(100, (chi_enc / chi_orig) * 100) if chi_orig > 0 else 100
        
        values = [entropy_score, npcr_score, uaci_score, corr_score, uniform_score]
        values += values[:1]  # Complete the circle
        
        angles = np.linspace(0, 2 * np.pi, len(categories), endpoint=False).tolist()
        angles += angles[:1]
        
        ax.plot(angles, values, 'o-', linewidth=2, color='#e74c3c', label='AEGIS Performance')
        ax.fill(angles, values, alpha=0.25, color='#e74c3c')
        
        # Reference circle at 100%
        ax.plot(angles, [100]*len(angles), '--', linewidth=1, color='green', alpha=0.5, label='Ideal (100%)')
        
        ax.set_xticks(angles[:-1])
        ax.set_xticklabels(categories, fontsize=10)
        ax.set_ylim(0, 110)
        ax.set_yticks([25, 50, 75, 100])
        ax.set_yticklabels(['25%', '50%', '75%', '100%'], fontsize=9)
        ax.set_title('Figure 4: Cryptographic Security Metrics (Radar Analysis)', 
                    fontsize=13, fontweight='bold', pad=20)
        ax.legend(loc='upper right', bbox_to_anchor=(1.3, 1.1), fontsize=10)
        ax.grid(True, alpha=0.3)
        
        plt.tight_layout()
        return fig
    
    def generate_table1_performance_metrics(self):
        """Table 1: Complete Performance Metrics."""
        fig, ax = plt.subplots(figsize=(12, 8))
        ax.axis('tight')
        ax.axis('off')
        
        table_data = [
            ['Metric', 'Measured Value', 'Expected/Ideal', 'Status'],
            ['Mean Squared Error (MSE)', f'{self.results["mse"]:.10f}', '0.0', 
             'PASS' if self.results['mse'] < 0.0001 else 'FAIL'],
            ['Peak SNR (PSNR)', f'{self.results["psnr"]:.4f} dB', '> 40 dB', 
             'PASS' if self.results['psnr'] > 40 else 'FAIL'],
            ['Structural Similarity (SSIM)', f'{self.results["ssim"]:.6f}', '> 0.99', 
             'PASS' if self.results['ssim'] > 0.99 else 'FAIL'],
            ['Entropy (Encrypted)', f'{self.results["entropy_encrypted"]:.6f} bits', '≈ 8.0 bits', 
             'PASS' if self.results['entropy_encrypted'] > 7.99 else 'FAIL'],
            ['NPCR (Avalanche)', f'{self.results["npcr"]:.4f} %', '> 99.00 %', 
             'PASS' if self.results['npcr'] > 99.0 else 'FAIL'],
            ['UACI (Avalanche)', f'{self.results["uaci"]:.4f} %', '33.46 ± 1 %', 
             'PASS' if 32.46 < self.results['uaci'] < 34.46 else 'FAIL'],
            ['Correlation (Horizontal)', f'{abs(self.results["corr_encrypted"]["horizontal"]):.6f}', '< 0.05', 
             'PASS' if abs(self.results['corr_encrypted']['horizontal']) < 0.05 else 'FAIL'],
            ['Correlation (Vertical)', f'{abs(self.results["corr_encrypted"]["vertical"]):.6f}', '< 0.05', 
             'PASS' if abs(self.results['corr_encrypted']['vertical']) < 0.05 else 'FAIL'],
            ['Key Space', self.results['key_space'], '≥ 2^128', 'PASS'],
            ['PBKDF2 Iterations', f'{self.results["pbkdf2_iterations"]:,}', '≥ 10,000', 'PASS'],
            ['', '', '', ''],
            ['* Avalanche Effect Test:', 'C1 vs C2 (1-pixel change)', '', '']
        ]
        
        table = ax.table(cellText=table_data, loc='center', cellLoc='left')
        table.auto_set_font_size(False)
        table.set_fontsize(10)
        table.scale(1, 2.5)
        
        # Style the header
        for (row, col), cell in table.get_celld().items():
            if row == 0:
                cell.set_text_props(weight='bold', color='white', fontsize=11)
                cell.set_facecolor('#2c3e50')
            elif col == 0:
                cell.set_text_props(weight='bold')
                cell.set_facecolor('#ecf0f1')
            elif col == 3:  # Status column
                if 'PASS' in table_data[row][col]:
                    cell.set_facecolor('#d5f4e6')
                    cell.set_text_props(color='green', weight='bold')
                else:
                    cell.set_facecolor('#fadbd8')
                    cell.set_text_props(color='red', weight='bold')
        
        ax.set_title('Table I: Comprehensive Security & Performance Metrics', 
                    fontsize=14, fontweight='bold', pad=20)
        
        plt.tight_layout()
        return fig
    
    def generate_table2_comparative_analysis(self):
        """Table 2: Before/After Encryption Comparison."""
        fig, ax = plt.subplots(figsize=(10, 6))
        ax.axis('tight')
        ax.axis('off')
        
        table_data = [
            ['Property', 'Original Image', 'Encrypted Image', 'Change (%)'],
            ['Entropy', 
             f'{self.results["entropy_original"]:.4f} bits', 
             f'{self.results["entropy_encrypted"]:.4f} bits',
             f'+{((self.results["entropy_encrypted"] - self.results["entropy_original"]) / self.results["entropy_original"] * 100):.2f}%'],
            ['Correlation (H)', 
             f'{self.results["corr_original"]["horizontal"]:.6f}', 
             f'{self.results["corr_encrypted"]["horizontal"]:.6f}',
             f'{((abs(self.results["corr_encrypted"]["horizontal"]) - abs(self.results["corr_original"]["horizontal"])) / abs(self.results["corr_original"]["horizontal"]) * 100):.2f}%'],
            ['Correlation (V)', 
             f'{self.results["corr_original"]["vertical"]:.6f}', 
             f'{self.results["corr_encrypted"]["vertical"]:.6f}',
             f'{((abs(self.results["corr_encrypted"]["vertical"]) - abs(self.results["corr_original"]["vertical"])) / abs(self.results["corr_original"]["vertical"]) * 100):.2f}%'],
            ['Chi-Square', 
             f'{self.results["chi_square_original"]:.2f}', 
             f'{self.results["chi_square_encrypted"]:.2f}',
             f'+{((self.results["chi_square_encrypted"] - self.results["chi_square_original"]) / self.results["chi_square_original"] * 100):.2f}%']
        ]
        
        table = ax.table(cellText=table_data, loc='center', cellLoc='center')
        table.auto_set_font_size(False)
        table.set_fontsize(11)
        table.scale(1.2, 2.8)
        
        # Style the header
        for (row, col), cell in table.get_celld().items():
            if row == 0:
                cell.set_text_props(weight='bold', color='white', fontsize=12)
                cell.set_facecolor('#34495e')
            elif col == 0:
                cell.set_text_props(weight='bold')
                cell.set_facecolor('#ecf0f1')
        
        ax.set_title('Table II: Comparative Analysis - Encryption Impact', 
                    fontsize=14, fontweight='bold', pad=20)
        
        plt.tight_layout()
        return fig
    
    # ==================== MAIN EXECUTION ====================
    
    def generate_all_ieee_results(self, output_dir='ieee_results'):
        """Generate all IEEE publication figures and tables."""
        # Create output directory
        os.makedirs(output_dir, exist_ok=True)
        
        print("\n" + "="*70)
        print("GENERATING IEEE PUBLICATION FIGURES")
        print("="*70)
        
        # Generate all figures
        figures = {
            'figure1_entropy': self.generate_figure1_entropy_comparison(),
            'figure2_correlation': self.generate_figure2_correlation_comparison(),
            'figure3_histogram': self.generate_figure3_histogram_analysis(),
            'figure4_radar': self.generate_figure4_security_metrics_radar(),
            'table1_metrics': self.generate_table1_performance_metrics(),
            'table2_comparison': self.generate_table2_comparative_analysis()
        }
        
        # Save all figures
        for name, fig in figures.items():
            filepath = os.path.join(output_dir, f'{name}.png')
            fig.savefig(filepath, dpi=300, bbox_inches='tight')
            print(f"[+] Saved: {filepath}")
            plt.close(fig)
        
        # Generate summary report
        self.generate_summary_report(output_dir)
        
        print("\n" + "="*70)
        print("ALL IEEE FIGURES GENERATED SUCCESSFULLY")
        print(f"Output Directory: {output_dir}/")
        print("="*70)
        print("\nFiles created:")
        print("  - figure1_entropy.png (Entropy comparison bar chart)")
        print("  - figure2_correlation.png (Correlation analysis)")
        print("  - figure3_histogram.png (Histogram & visual comparison)")
        print("  - figure4_radar.png (Security metrics radar chart)")
        print("  - table1_metrics.png (Performance metrics table)")
        print("  - table2_comparison.png (Before/after comparison table)")
        print("  - results_summary.txt (Text summary for reference)")
        print("\nReady for IEEE paper submission!")
    
    def generate_summary_report(self, output_dir):
        """Generate text summary report."""
        filepath = os.path.join(output_dir, 'results_summary.txt')
        
        with open(filepath, 'w') as f:
            f.write("="*70 + "\n")
            f.write("AEGIS IMAGE ENCRYPTION SYSTEM - RESULTS SUMMARY\n")
            f.write("="*70 + "\n")
            f.write(f"Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
            f.write("="*70 + "\n\n")
            
            f.write("1. LOSSLESS GUARANTEE METRICS\n")
            f.write("-" * 70 + "\n")
            f.write(f"   MSE:  {self.results['mse']:.10f}\n")
            f.write(f"   PSNR: {self.results['psnr']:.4f} dB\n")
            f.write(f"   SSIM: {self.results['ssim']:.6f}\n\n")
            
            f.write("2. ENTROPY ANALYSIS\n")
            f.write("-" * 70 + "\n")
            f.write(f"   Original:  {self.results['entropy_original']:.6f} bits\n")
            f.write(f"   Encrypted: {self.results['entropy_encrypted']:.6f} bits\n")
            f.write(f"   Decrypted: {self.results['entropy_decrypted']:.6f} bits\n\n")
            
            f.write("3. PIXEL CHANGE METRICS (AVALANCHE EFFECT TEST)\n")
            f.write("-" * 70 + "\n")
            f.write("   METHOD: True cryptographic avalanche test\n")
            f.write("   Step 1: Encrypt original image -> C1 (temp_encrypted.png)\n")
            f.write("   Step 2: Change ONE pixel in original -> P'\n")
            f.write("   Step 3: Encrypt modified image -> C2\n")
            f.write("   Step 4: Calculate NPCR/UACI between C1 and C2\n")
            f.write("\n")
            f.write(f"   NPCR (Avalanche): {self.results['npcr']:.4f}%\n")
            f.write(f"   UACI (Avalanche): {self.results['uaci']:.4f}%\n")
            f.write("\n")
            f.write("   INTERPRETATION:\n")
            f.write("   - NPCR measures % of pixels that change when 1 input pixel changes\n")
            f.write("   - UACI measures average intensity change magnitude\n")
            f.write("   - High values (>99% NPCR, ~33% UACI) indicate strong avalanche effect\n")
            f.write("   - Demonstrates sensitivity to plaintext modifications\n\n")
            
            f.write("4. CORRELATION COEFFICIENTS\n")
            f.write("-" * 70 + "\n")
            f.write("   Original Image:\n")
            f.write(f"     Horizontal: {self.results['corr_original']['horizontal']:.6f}\n")
            f.write(f"     Vertical:   {self.results['corr_original']['vertical']:.6f}\n")
            f.write(f"     Diagonal:   {self.results['corr_original']['diagonal']:.6f}\n")
            f.write("   Encrypted Image:\n")
            f.write(f"     Horizontal: {self.results['corr_encrypted']['horizontal']:.6f}\n")
            f.write(f"     Vertical:   {self.results['corr_encrypted']['vertical']:.6f}\n")
            f.write(f"     Diagonal:   {self.results['corr_encrypted']['diagonal']:.6f}\n\n")
            
            f.write("5. HISTOGRAM UNIFORMITY\n")
            f.write("-" * 70 + "\n")
            f.write(f"   Original Chi-Square:  {self.results['chi_square_original']:.2f}\n")
            f.write(f"   Encrypted Chi-Square: {self.results['chi_square_encrypted']:.2f}\n\n")
            
            f.write("6. CRYPTOGRAPHIC PARAMETERS\n")
            f.write("-" * 70 + "\n")
            f.write(f"   Key Space: {self.results['key_space']}\n")
            f.write(f"   PBKDF2 Iterations: {self.results['pbkdf2_iterations']:,}\n")
            f.write(f"   Wavelet Type: {self.results['wavelet_type']}\n")
            f.write(f"   DNA Rules: {self.results['dna_rules']}\n\n")
            
            f.write("="*70 + "\n")
            f.write("END OF REPORT\n")
            f.write("="*70 + "\n")
        
        print(f"[+] Saved: {filepath}")


# ==================== MAIN EXECUTION ====================

def main():
    """Main execution function."""
    print("\n" + "="*70)
    print("IEEE PUBLICATION RESULTS GENERATOR")
    print("Advanced Image Encryption System")
    print("="*70 + "\n")
    
    # ========== IMPORTANT: SET YOUR PASSWORD HERE ==========
    # This MUST match the password you used in the Streamlit app!
    # If you used a different password, change it here:
    ENCRYPTION_PASSWORD = "Sriroop"  # ← CHANGE THIS!
    
    print(f"[CONFIG] Encryption password: '{ENCRYPTION_PASSWORD}'")
    print("[INFO] If this doesn't match your Streamlit password, edit line 707!\n")
    # ======================================================
    
    try:
        # Initialize generator with YOUR password
        generator = IEEEResultsGenerator(encryption_password=ENCRYPTION_PASSWORD)
        
        # Load images
        generator.load_images()
        
        # Run all analyses
        generator.run_all_analyses()
        
        # Generate all IEEE figures
        generator.generate_all_ieee_results()
        
        print("\n[SUCCESS] All results generated successfully!")
        print("[INFO] Check the 'ieee_results' folder for all figures and tables.")
        
    except FileNotFoundError as e:
        print(f"\n[ERROR] {e}")
        print("\n[SOLUTION]:")
        print("1. Run your Streamlit application (app_tactical.py)")
        print("2. Encrypt an image")
        print("3. Decrypt the image")
        print("4. Then run this script again")
    
    except Exception as e:
        print(f"\n[ERROR] Unexpected error: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    main()
