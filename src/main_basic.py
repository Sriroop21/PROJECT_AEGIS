"""

SYSTEM ARCHITECTURE:
1. Wavelet Transform: Lossless integer Haar (structure separation)
2. Chaos Generator: Lorenz system (cryptographic key stream)
3. DNA Encoder: 8-rule biological operations (confusion/diffusion)
4. Cross-Band Encryption: Master-slave protocol (NOVEL CONTRIBUTION)

WORKFLOW:
Input Image → Wavelet → Cross-Band Encrypt → Spatial Stack → Encrypted Image
Encrypted Image → Spatial Unstack → Cross-Band Decrypt → Wavelet Inverse → Original Image

SECURITY FEATURES:
- Key space: 2^256 (password-derived)
- Lossless transform: Zero reconstruction error
- Adaptive encryption: Structure-aware dual-mode
- Hierarchical dependency: LL controls LH/HL/HH

"""

import cv2
import numpy as np
import os
import time
import pickle
import matplotlib.pyplot as plt
from typing import Tuple, Dict, Optional

# Import our cryptographic modules (using correct class names without "Advanced")
from wavelet_processor import WaveletProcessor
from cross_band_encryption import CrossBandEncryption


class AdvancedImageEncryptionSystem:
    """
    
    Features:
    - RGB and grayscale support
    - Channel-independent encryption (prevents color correlation attacks)
    - Metadata persistence (for perfect decryption)
    - Security metrics calculation
    - Performance benchmarking
    """
    
    def __init__(self, password: str, salt: Optional[str] = None):
        """
        Initialize encryption system.
        
        Args:
            password: Encryption password (recommend 12+ characters)
            salt: Optional salt for key derivation
        """
        if not password:
            raise ValueError("Password cannot be empty")
        
        print(f"\n{'='*70}")
        print(f"INITIALIZING ADVANCED IMAGE ENCRYPTION SYSTEM")
        print(f"{'='*70}")
        print(f"[System] Password: {'*' * len(password)}")
        print(f"[System] Salt: {salt if salt else 'Default'}")
        
        # Initialize cryptographic components
        self.password = password
        self.salt = salt
        
        # Lossless wavelet processor
        self.wavelet = WaveletProcessor(wavelet='haar')
        
        # Cross-band encryption engine
        self.crypto = CrossBandEncryption(password, salt=salt)
        
        # Metadata storage (needed for decryption)
        self.metadata = {}
        
        print(f"[System] ✓ All modules initialized")
        print(f"{'='*70}\n")
    
    def encrypt_image(
        self,
        input_path: str,
        output_path: str,
        metadata_path: Optional[str] = None,
        verbose: bool = True
    ) -> np.ndarray:
        """
        Encrypt an image using structure-aware cross-band encryption.
        
        ENCRYPTION PIPELINE:
        1. Load image (RGB or grayscale)
        2. Split into channels
        3. For each channel:
           a. Wavelet decomposition (LL, LH, HL, HH)
           b. Cross-band encryption (LL controls detail encryption)
           c. Spatial packaging (stack bands: [LL|LH] over [HL|HH])
        4. Merge channels
        5. Save encrypted image + metadata
        
        CRITICAL: We do NOT apply inverse wavelet to encrypted bands.
        Encrypted bands are random noise - applying IDWT would cause overflow
        and data loss when clipping to [0,255]. Instead, we stack bands spatially
        to create a lossless "package" that preserves all encrypted data.
        
        Args:
            input_path: Path to original image
            output_path: Path to save encrypted image
            metadata_path: Optional path to save metadata (auto-generated if None)
            verbose: If True, print detailed progress
        
        Returns:
            Encrypted image as numpy array
        
        Raises:
            FileNotFoundError: If input image doesn't exist
            ValueError: If image format is invalid
        """
        start_time = time.time()
        
        if verbose:
            print(f"\n{'='*70}")
            print(f"ENCRYPTION STARTED")
            print(f"{'='*70}")
            print(f"[Input]  {input_path}")
            print(f"[Output] {output_path}")
        
        # Load image
        img = cv2.imread(input_path, cv2.IMREAD_UNCHANGED)
        if img is None:
            raise FileNotFoundError(f"Image not found: {input_path}")
        
        # Detect image type
        if len(img.shape) == 2:
            # Grayscale
            channels = [img]
            is_rgb = False
            if verbose:
                print(f"[Image] Grayscale: {img.shape}")
        elif len(img.shape) == 3:
            # RGB
            channels = cv2.split(img)
            is_rgb = True
            if verbose:
                print(f"[Image] RGB: {img.shape} → {len(channels)} channels")
        else:
            raise ValueError(f"Unsupported image shape: {img.shape}")
        
        # Store metadata
        self.metadata = {
            'is_rgb': is_rgb,
            'original_shape': img.shape,
            'num_channels': len(channels),
            'channel_data': []
        }
        
        encrypted_channels = []
        
        # Encrypt each channel independently
        for ch_idx, channel in enumerate(channels):
            if verbose:
                print(f"\n[Channel {ch_idx+1}/{len(channels)}] Processing...")
            
            # CRITICAL SECURITY FIX: Generate unique chaotic key stream per channel
            # This prevents the "ECB Penguin" vulnerability where identical pixels
            # in different channels encrypt to the same value, revealing patterns.
            # 
            # Method: Channel-specific salt derivation
            # - Each channel gets unique salt: "salt_ch_0", "salt_ch_1", etc.
            # - Different salts → different initial conditions → different key streams
            # - Prevents correlation attacks across color channels
            channel_salt = f"{self.salt}_channel_{ch_idx}"
            self.crypto = CrossBandEncryption(self.password, salt=channel_salt)
            
            if verbose:
                print(f"  [Security] Channel-specific key stream initialized")
            
            # Step 1: Wavelet decomposition
            if verbose:
                print(f"  [Step 1] Wavelet decomposition...")
            
            bands, wav_params = self.wavelet.decompose(channel)
            LL, LH, HL, HH = bands
            
            if verbose:
                print(f"    LL: {LL.shape}, LH: {LH.shape}, HL: {HL.shape}, HH: {HH.shape}")
            
            # Step 2: Cross-band encryption (THE NOVELTY)
            if verbose:
                print(f"  [Step 2] Cross-band encryption (adaptive)...")
            
            (LL_enc, LH_enc, HL_enc, HH_enc), threshold = self.crypto.encrypt(
                LL, LH, HL, HH, verbose=False
            )
            
            if verbose:
                print(f"    Threshold: {threshold:.2f}")
            
            # Step 3: SPATIAL PACKAGING (NOT inverse wavelet!)
            # CRITICAL: Encrypted bands are random noise - CANNOT go through IDWT
            # Instead, we stack them spatially to preserve all encrypted data
            if verbose:
                print(f"  [Step 3] Spatial packaging (stacking encrypted bands)...")
            
            # Stack bands: [LL | LH] on top, [HL | HH] on bottom
            # Note: Bands are already bit-packed (double width from lossless wavelet)
            top_row = np.hstack((LL_enc, LH_enc))
            bottom_row = np.hstack((HL_enc, HH_enc))
            enc_channel = np.vstack((top_row, bottom_row))
            
            if verbose:
                print(f"    Packed shape: {enc_channel.shape}")
            
            encrypted_channels.append(enc_channel)
            
            # Store channel-specific metadata
            self.metadata['channel_data'].append({
                'wavelet_params': wav_params,
                'threshold': threshold
            })
            
            if verbose:
                print(f"  ✓ Channel {ch_idx+1} encrypted")
        
        # Merge channels
        if is_rgb:
            encrypted_image = cv2.merge(encrypted_channels)
        else:
            encrypted_image = encrypted_channels[0]
        
        # Save encrypted image
        cv2.imwrite(output_path, encrypted_image)
        
        # Save metadata
        if metadata_path is None:
            metadata_path = output_path.replace('.png', '_metadata.pkl')
        
        with open(metadata_path, 'wb') as f:
            pickle.dump(self.metadata, f)
        
        elapsed = time.time() - start_time
        
        if verbose:
            print(f"\n{'='*70}")
            print(f"ENCRYPTION COMPLETE")
            print(f"{'='*70}")
            print(f"[Time] {elapsed:.3f} seconds")
            print(f"[Throughput] {img.size / elapsed:,.0f} pixels/second")
            print(f"[Output] {output_path}")
            print(f"[Metadata] {metadata_path}")
            print(f"{'='*70}\n")
        
        return encrypted_image
    
    def decrypt_image(
        self,
        encrypted_path: str,
        output_path: str,
        metadata_path: Optional[str] = None,
        verbose: bool = True
    ) -> np.ndarray:
        """
        Decrypt an encrypted image.
        
        DECRYPTION PIPELINE:
        1. Load encrypted image + metadata
        2. Split into channels
        3. For each channel:
           a. Spatial unpackaging (extract [LL|LH] and [HL|HH])
           b. Cross-band decryption (LL decrypted first, then details)
           c. Wavelet reconstruction (frequency domain → spatial domain)
        4. Merge channels
        5. Save decrypted image
        
        CRITICAL: Encrypted image contains spatially stacked bands, NOT
        a wavelet-reconstructed image. We must unstack before decryption.
        
        Args:
            encrypted_path: Path to encrypted image
            output_path: Path to save decrypted image
            metadata_path: Path to metadata file (auto-detected if None)
            verbose: If True, print detailed progress
        
        Returns:
            Decrypted image as numpy array
        
        Raises:
            FileNotFoundError: If encrypted image or metadata not found
            ValueError: If metadata is corrupted
        """
        start_time = time.time()
        
        if verbose:
            print(f"\n{'='*70}")
            print(f"DECRYPTION STARTED")
            print(f"{'='*70}")
            print(f"[Input]  {encrypted_path}")
            print(f"[Output] {output_path}")
        
        # Load encrypted image
        img = cv2.imread(encrypted_path, cv2.IMREAD_UNCHANGED)
        if img is None:
            raise FileNotFoundError(f"Encrypted image not found: {encrypted_path}")
        
        # Load metadata
        if metadata_path is None:
            metadata_path = encrypted_path.replace('.png', '_metadata.pkl')
        
        if not os.path.exists(metadata_path):
            raise FileNotFoundError(f"Metadata not found: {metadata_path}")
        
        with open(metadata_path, 'rb') as f:
            self.metadata = pickle.load(f)
        
        if verbose:
            print(f"[Metadata] Loaded from {metadata_path}")
        
        # Split channels
        if self.metadata['is_rgb']:
            channels = cv2.split(img)
        else:
            channels = [img]
        
        if verbose:
            print(f"[Image] {len(channels)} channel(s)")
        
        decrypted_channels = []
        
        # Decrypt each channel
        for ch_idx, channel in enumerate(channels):
            if verbose:
                print(f"\n[Channel {ch_idx+1}/{len(channels)}] Processing...")
            
            # CRITICAL SECURITY FIX: Regenerate exact same channel-specific key stream
            # Must match the salt used during encryption for this channel
            channel_salt = f"{self.salt}_channel_{ch_idx}"
            self.crypto = CrossBandEncryption(self.password, salt=channel_salt)
            
            if verbose:
                print(f"  [Security] Channel-specific key stream regenerated")
            
            # Get channel metadata
            ch_metadata = self.metadata['channel_data'][ch_idx]
            wav_params = ch_metadata['wavelet_params']
            threshold = ch_metadata['threshold']
            
            # Step 1: SPATIAL UNPACKAGING
            # CRITICAL: Encrypted image is spatially stacked bands, not wavelet domain
            if verbose:
                print(f"  [Step 1] Spatial unpackaging (extracting encrypted bands)...")
            
            # Get band dimensions from metadata
            # Original bands were bit-packed (double width)
            h, w = channel.shape
            band_h = h // 2
            band_w = w // 2
            
            # Unstack: [LL | LH] top row, [HL | HH] bottom row
            LL_enc = channel[:band_h, :band_w]
            LH_enc = channel[:band_h, band_w:]
            HL_enc = channel[band_h:, :band_w]
            HH_enc = channel[band_h:, band_w:]
            
            if verbose:
                print(f"    Extracted bands: {LL_enc.shape}")
            
            # Step 2: Cross-band decryption
            if verbose:
                print(f"  [Step 2] Cross-band decryption...")
                print(f"    Using threshold: {threshold:.2f}")
            
            LL_dec, LH_dec, HL_dec, HH_dec = self.crypto.decrypt(
                LL_enc, LH_enc, HL_enc, HH_enc,
                threshold=threshold,
                verbose=False
            )
            
            # Step 3: Wavelet reconstruction
            if verbose:
                print(f"  [Step 3] Inverse wavelet transform...")
            
            dec_channel = self.wavelet.reconstruct(
                (LL_dec, LH_dec, HL_dec, HH_dec),
                wav_params
            )
            
            decrypted_channels.append(dec_channel)
            
            if verbose:
                print(f"  ✓ Channel {ch_idx+1} decrypted")
        
        # Merge channels
        if self.metadata['is_rgb']:
            decrypted_image = cv2.merge(decrypted_channels)
        else:
            decrypted_image = decrypted_channels[0]
        
        # Save decrypted image
        cv2.imwrite(output_path, decrypted_image)
        
        elapsed = time.time() - start_time
        
        if verbose:
            print(f"\n{'='*70}")
            print(f"DECRYPTION COMPLETE")
            print(f"{'='*70}")
            print(f"[Time] {elapsed:.3f} seconds")
            print(f"[Output] {output_path}")
            print(f"{'='*70}\n")
        
        return decrypted_image
    
    def analyze_security(
        self,
        original_path: str,
        encrypted_path: str,
        output_dir: str,
        decrypted_path: Optional[str] = None
    ) -> Dict:
        """
        Comprehensive security analysis.
        
        Metrics:
        1. Histogram analysis (uniformity)
        2. Correlation analysis (pixel relationships)
        3. Entropy (randomness)
        4. NPCR (Number of Pixel Change Rate)
        5. UACI (Unified Average Change Intensity)
        6. Reconstruction quality (if decrypted image provided)
        
        Args:
            original_path: Path to original image
            encrypted_path: Path to encrypted image
            output_dir: Directory to save analysis results
            decrypted_path: Optional path to decrypted image (for validation)
        
        Returns:
            Dictionary containing all security metrics
        """
        print(f"\n{'='*70}")
        print(f"SECURITY ANALYSIS")
        print(f"{'='*70}")
        
        # Load images WITHOUT any conversion (preserve original RGB data)
        original = cv2.imread(original_path, cv2.IMREAD_UNCHANGED)
        encrypted = cv2.imread(encrypted_path, cv2.IMREAD_UNCHANGED)
        
        if original is None or encrypted is None:
            raise FileNotFoundError("Could not load images for analysis")
        
        metrics = {}
        
        # 1. Histogram Analysis
        print(f"\n[1/6] Histogram Analysis...")
        
        fig, axes = plt.subplots(1, 2, figsize=(14, 5))
        
        axes[0].hist(original.ravel(), 256, [0, 256], color='blue', alpha=0.7)
        axes[0].set_title('Original Image Histogram', fontsize=14, fontweight='bold')
        axes[0].set_xlabel('Pixel Value')
        axes[0].set_ylabel('Frequency')
        axes[0].grid(alpha=0.3)
        
        axes[1].hist(encrypted.ravel(), 256, [0, 256], color='red', alpha=0.7)
        axes[1].set_title('Encrypted Image Histogram', fontsize=14, fontweight='bold')
        axes[1].set_xlabel('Pixel Value')
        axes[1].set_ylabel('Frequency')
        axes[1].grid(alpha=0.3)
        
        plt.tight_layout()
        hist_path = os.path.join(output_dir, 'histogram_analysis.png')
        plt.savefig(hist_path, dpi=300, bbox_inches='tight')
        plt.close()
        
        print(f"  ✓ Saved to {hist_path}")
        
        # 2. Correlation Analysis
        print(f"\n[2/6] Correlation Analysis...")
        
        # Handle size mismatch - use [:2] to safely unpack height and width from 2D or 3D arrays
        h_orig, w_orig = original.shape[:2]
        h_enc, w_enc = encrypted.shape[:2]
        
        if h_enc != h_orig or w_enc != w_orig:
            encrypted_cropped = encrypted[:h_orig, :w_orig]
        else:
            encrypted_cropped = encrypted
        
        # Horizontal correlation
        orig_h_corr = np.corrcoef(original[:, :-1].ravel(), original[:, 1:].ravel())[0, 1]
        enc_h_corr = np.corrcoef(encrypted_cropped[:, :-1].ravel(), encrypted_cropped[:, 1:].ravel())[0, 1]
        
        # Vertical correlation
        orig_v_corr = np.corrcoef(original[:-1, :].ravel(), original[1:, :].ravel())[0, 1]
        enc_v_corr = np.corrcoef(encrypted_cropped[:-1, :].ravel(), encrypted_cropped[1:, :].ravel())[0, 1]
        
        # Diagonal correlation
        orig_d_corr = np.corrcoef(original[:-1, :-1].ravel(), original[1:, 1:].ravel())[0, 1]
        enc_d_corr = np.corrcoef(encrypted_cropped[:-1, :-1].ravel(), encrypted_cropped[1:, 1:].ravel())[0, 1]
        
        metrics['correlation'] = {
            'original': {'horizontal': orig_h_corr, 'vertical': orig_v_corr, 'diagonal': orig_d_corr},
            'encrypted': {'horizontal': enc_h_corr, 'vertical': enc_v_corr, 'diagonal': enc_d_corr}
        }
        
        print(f"  Original - H: {orig_h_corr:.6f}, V: {orig_v_corr:.6f}, D: {orig_d_corr:.6f}")
        print(f"  Encrypted - H: {enc_h_corr:.6f}, V: {enc_v_corr:.6f}, D: {enc_d_corr:.6f}")
        
        # 3. Entropy
        print(f"\n[3/6] Entropy Analysis...")
        
        def calculate_entropy(img):
            hist, _ = np.histogram(img.ravel(), bins=256, range=(0, 256))
            hist = hist[hist > 0]
            probs = hist / np.sum(hist)
            return -np.sum(probs * np.log2(probs))
        
        orig_entropy = calculate_entropy(original)
        # Use full encrypted image for entropy (all pixels are encrypted noise)
        enc_entropy = calculate_entropy(encrypted)
        
        metrics['entropy'] = {
            'original': orig_entropy,
            'encrypted': enc_entropy
        }
        
        print(f"  Original: {orig_entropy:.6f} bits")
        print(f"  Encrypted: {enc_entropy:.6f} bits (Ideal: 8.0)")
        
        # 4. NPCR (Number of Pixel Change Rate)
        print(f"\n[4/6] NPCR Analysis...")
        
        # CRITICAL FIX: Encrypted image is larger due to spatial packaging
        # We need to compare same-sized regions
        # Take only the region that corresponds to original image size
        h_orig, w_orig = original.shape[:2]
        h_enc, w_enc = encrypted.shape[:2]
        
        # If encrypted is larger (spatial packaging), crop to original size for comparison
        if h_enc != h_orig or w_enc != w_orig:
            print(f"  Note: Encrypted image ({h_enc}x{w_enc}) vs Original ({h_orig}x{w_orig})")
            # Take top-left region matching original size
            encrypted_cropped = encrypted[:h_orig, :w_orig]
        else:
            encrypted_cropped = encrypted
        
        changed_pixels = np.sum(original != encrypted_cropped)
        total_pixels = original.size
        npcr = (changed_pixels / total_pixels) * 100
        
        metrics['npcr'] = npcr
        
        print(f"  NPCR: {npcr:.4f}% (Ideal: >99%)")
        
        # 5. UACI (Unified Average Change Intensity)
        print(f"\n[5/6] UACI Analysis...")
        
        # Use cropped encrypted image for fair comparison
        if h_enc != h_orig or w_enc != w_orig:
            encrypted_cropped = encrypted[:h_orig, :w_orig]
        else:
            encrypted_cropped = encrypted
        
        uaci = np.sum(np.abs(original.astype(float) - encrypted_cropped.astype(float))) / (total_pixels * 255) * 100
        
        metrics['uaci'] = uaci
        
        print(f"  UACI: {uaci:.4f}% (Ideal: ~33%)")
        
        # 6. Reconstruction Quality (if decrypted image provided)
        if decrypted_path and os.path.exists(decrypted_path):
            print(f"\n[6/6] Reconstruction Quality...")
            
            decrypted = cv2.imread(decrypted_path, cv2.IMREAD_UNCHANGED)
            
            if decrypted is not None:
                # Ensure same dimensions - use [:2] for 2D or 3D arrays
                h, w = original.shape[:2]
                h_dec, w_dec = decrypted.shape[:2]
                
                if h_dec != h or w_dec != w:
                    print(f"  Warning: Size mismatch - Original: {original.shape}, Decrypted: {decrypted.shape}")
                    # Crop if needed
                    decrypted = decrypted[:h, :w]
                
                # MSE and PSNR on raw arrays (handles 2D or 3D automatically via ravel)
                mse = np.mean((original.astype(float) - decrypted.astype(float)) ** 2)
                
                if mse == 0:
                    psnr = 100.0
                else:
                    psnr = 10 * np.log10(255**2 / mse)
                
                # Perfect reconstruction check (compares raw bytes)
                perfect = np.array_equal(original, decrypted)
                
                metrics['reconstruction'] = {
                    'mse': mse,
                    'psnr': psnr,
                    'perfect': perfect
                }
                
                print(f"  MSE: {mse:.6f}")
                print(f"  PSNR: {psnr:.2f} dB")
                print(f"  Perfect: {perfect}")
        
        # Generate summary report
        print(f"\n{'='*70}")
        print(f"SECURITY METRICS SUMMARY")
        print(f"{'='*70}")
        print(f"Correlation Reduction:")
        print(f"  Horizontal: {orig_h_corr:.4f} → {enc_h_corr:.4f}")
        print(f"  Vertical:   {orig_v_corr:.4f} → {enc_v_corr:.4f}")
        print(f"  Diagonal:   {orig_d_corr:.4f} → {enc_d_corr:.4f}")
        print(f"\nRandomness:")
        print(f"  Entropy: {enc_entropy:.4f} / 8.0 bits ({enc_entropy/8*100:.2f}%)")
        print(f"\nDiffusion:")
        print(f"  NPCR: {npcr:.2f}% (target: >99%)")
        print(f"  UACI: {uaci:.2f}% (target: ~33%)")
        print(f"{'='*70}\n")
        
        return metrics


# Main execution
if __name__ == "__main__":
    print(f"\n{'='*70}")
    print(f"STRUCTURE-AWARE IMAGE ENCRYPTION SYSTEM")
    print(f"Novel Cross-Band Hierarchical Encryption")
    print(f"{'='*70}\n")
    
    # Setup paths
    current_dir = os.path.dirname(os.path.abspath(__file__))
    project_root = os.path.dirname(current_dir)
    
    data_dir = os.path.join(project_root, 'data')
    results_dir = os.path.join(project_root, 'results')
    
    os.makedirs(data_dir, exist_ok=True)
    os.makedirs(results_dir, exist_ok=True)
    
    # Define file paths
    input_filename = "lena.png"
    input_path = os.path.join(data_dir, input_filename)
    encrypted_path = os.path.join(results_dir, "encrypted.png")
    decrypted_path = os.path.join(results_dir, "decrypted.png")
    
    # Create test image if needed
    if not os.path.exists(input_path):
        print(f"[Info] '{input_filename}' not found. Creating test image...")
        test_img = np.zeros((256, 256, 3), dtype=np.uint8)
        
        # Gradient
        for i in range(256):
            test_img[i, :, :] = i
        
        # Shapes
        cv2.circle(test_img, (128, 128), 60, (255, 255, 255), -1)
        cv2.rectangle(test_img, (50, 50), (100, 100), (0, 0, 255), -1)
        
        cv2.imwrite(input_path, test_img)
        print(f"[Info] Test image created: {input_path}")
    
    # Initialize system
    system = AdvancedImageEncryptionSystem(
        password="SecurePassword2026",
        salt="ImageEncryptionProject"
    )
    
    # Encrypt
    encrypted_img = system.encrypt_image(
        input_path=input_path,
        output_path=encrypted_path,
        verbose=True
    )
    
    # Decrypt
    decrypted_img = system.decrypt_image(
        encrypted_path=encrypted_path,
        output_path=decrypted_path,
        verbose=True
    )
    
    # Security analysis
    metrics = system.analyze_security(
        original_path=input_path,
        encrypted_path=encrypted_path,
        output_dir=results_dir,
        decrypted_path=decrypted_path
    )
    
    print(f"\n{'='*70}")
    print(f"SYSTEM TEST COMPLETE")
    print(f"{'='*70}")
    print(f"[Results Directory] {results_dir}")
    print(f"  - encrypted.png")
    print(f"  - decrypted.png")
    print(f"  - histogram_analysis.png")
    print(f"  - encrypted_metadata.pkl")
    print(f"{'='*70}\n")
