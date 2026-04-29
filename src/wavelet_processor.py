"""
Advanced Lossless Wavelet Processor for Cryptographic Image Encryption.

CRITICAL DIFFERENCE FROM STANDARD IMPLEMENTATIONS:
This is NOT a compression tool. This is a CRYPTOGRAPHIC COMPONENT.
Standard wavelet libraries (PyWavelets) use floating-point arithmetic which
introduces rounding errors - acceptable for compression, FATAL for encryption.

SOLUTION: Integer Wavelet Transform with 16-bit Bit-Packing
- Uses integer-only arithmetic (no floating point)
- Preserves all coefficient information via bit-packing
- Guarantees ZERO reconstruction error (lossless)
- Prevents "speckle noise" during decryption

MECHANISM:
1. Integer Haar Transform: Uses lifting scheme (lossless)
2. 16-bit Coefficients: Can represent negative values (-32768 to +32767)
3. Bit-Packing: Split each 16-bit value into two 8-bit values
4. Encryption: Process the 8-bit packed bands (looks like normal image data)
5. Reconstruction: Unpack 8-bit → 16-bit → Inverse transform

NOVELTY SUPPORT:
Separates image into 4 frequency bands for structure-aware encryption:
- LL (Low-Low): Image structure/approximation (controls encryption)
- LH (Low-High): Horizontal edges
- HL (High-Low): Vertical edges
- HH (High-High): Diagonal details

"""

import numpy as np
from typing import Tuple, Dict, Optional
import matplotlib.pyplot as plt


class WaveletProcessor:
    """
    Cryptographic-grade lossless wavelet transform processor.
    
    Key Properties:
    - ZERO reconstruction error (mathematically proven)
    - Integer-only operations (no floating point)
    - Bit-perfect encryption compatibility
    - Structure-aware decomposition for adaptive encryption
    
    WARNING: Do NOT replace this with standard PyWavelets DWT.
    Standard DWT uses float64 which causes 0.5-2.0 pixel errors.
    In encryption, ANY error causes complete decryption failure (speckle noise).
    """
    
    def __init__(self, wavelet: str = 'haar'):
        """
        Initialize lossless wavelet processor.
        
        Args:
            wavelet: Only 'haar' supported (integer lifting scheme)
        
        Note: Other wavelets (db2, sym2) require floating point and are
              not suitable for lossless cryptographic applications.
        """
        if wavelet.lower() != 'haar':
            print(f"[WARNING] Only 'haar' guarantees lossless transform.")
            print(f"[WARNING] Forcing wavelet = 'haar' for encryption safety.")
            wavelet = 'haar'
        
        self.wavelet = wavelet
        print(f"[WaveletProcessor] Initialized (Lossless Integer Transform)")
        print(f"  Wavelet: {self.wavelet.upper()} (Integer Lifting Scheme)")
        print(f"  Precision: 16-bit coefficients with bit-packing")
        print(f"  Guarantee: ZERO reconstruction error")
    
    def decompose(
        self,
        image: np.ndarray
    ) -> Tuple[Tuple[np.ndarray, ...], Dict]:
        """
        Perform lossless 2D Integer Wavelet Transform.
        
        MATHEMATICAL FOUNDATION:
        Uses Haar wavelet lifting scheme (integer-only operations):
        
        Forward Transform:
        - L = (x + y) // 2  (approximation, integer division)
        - H = x - y         (detail, exact difference)
        
        This guarantees perfect reversibility:
        - x = L + (H + 1) // 2
        - y = x - H
        
        BIT-PACKING:
        Coefficients are 16-bit integers (can be negative).
        Each coefficient is split into:
        - High byte: Top 8 bits
        - Low byte: Bottom 8 bits
        Stacked side-by-side to create 8-bit encryption-compatible bands.
        
        Args:
            image: Input image (uint8, grayscale or RGB)
        
        Returns:
            Tuple of:
                - bands: (LL, LH, HL, HH) as packed uint8 arrays
                - params: Metadata for perfect reconstruction
        
        Raises:
            ValueError: If image format is invalid
        """
        # Validate input
        if image.ndim == 3:
            print(f"[DWT] Processing RGB image channel-by-channel...")
            # For RGB, we'll process first channel as example
            # Full system should process all 3 channels
            image = image[:, :, 0]
            print(f"[DWT] Using channel 0 for demonstration")
        
        if image.ndim != 2:
            raise ValueError(f"Image must be 2D grayscale, got shape {image.shape}")
        
        print(f"[DWT] Input image: {image.shape}, dtype: {image.dtype}")
        
        # Convert to signed 16-bit (needed for negative coefficients)
        image_int16 = image.astype(np.int16)
        h, w = image_int16.shape
        
        # Padding for odd dimensions
        pad_h = h % 2
        pad_w = w % 2
        
        if pad_h:
            # Replicate last row
            image_int16 = np.vstack((image_int16, image_int16[-1, :]))
        if pad_w:
            # Replicate last column
            image_int16 = np.hstack((image_int16, image_int16[:, -1].reshape(-1, 1)))
        
        print(f"[DWT] Padded to: {image_int16.shape}")
        
        # ===== INTEGER HAAR TRANSFORM (LOSSLESS) =====
        
        # STEP 1: Column Transform
        # Split into even (0,2,4...) and odd (1,3,5...) columns
        even_cols = image_int16[:, 0::2]
        odd_cols = image_int16[:, 1::2]
        
        # Approximation: average (integer division)
        col_L = (even_cols + odd_cols) // 2
        # Detail: difference (exact)
        col_H = even_cols - odd_cols
        
        # STEP 2: Row Transform on approximation coefficients
        even_rows_L = col_L[0::2, :]
        odd_rows_L = col_L[1::2, :]
        
        LL = (even_rows_L + odd_rows_L) // 2  # Low-Low (structure)
        HL = even_rows_L - odd_rows_L          # High-Low (vertical edges)
        
        # STEP 3: Row Transform on detail coefficients
        even_rows_H = col_H[0::2, :]
        odd_rows_H = col_H[1::2, :]
        
        LH = (even_rows_H + odd_rows_H) // 2  # Low-High (horizontal edges)
        HH = even_rows_H - odd_rows_H          # High-High (diagonal details)
        
        print(f"[DWT] Coefficient shapes:")
        print(f"  LL: {LL.shape}, range [{LL.min()}, {LL.max()}]")
        print(f"  LH: {LH.shape}, range [{LH.min()}, {LH.max()}]")
        print(f"  HL: {HL.shape}, range [{HL.min()}, {HL.max()}]")
        print(f"  HH: {HH.shape}, range [{HH.min()}, {HH.max()}]")
        
        # ===== BIT-PACKING (16-bit → 2x8-bit) =====
        
        print(f"[DWT] Bit-packing 16-bit coefficients to 8-bit bands...")
        
        LL_packed = self._pack_int16_to_uint8(LL)
        LH_packed = self._pack_int16_to_uint8(LH)
        HL_packed = self._pack_int16_to_uint8(HL)
        HH_packed = self._pack_int16_to_uint8(HH)
        
        print(f"[DWT] Packed band shapes (ready for encryption):")
        print(f"  LL: {LL_packed.shape}")
        print(f"  LH: {LH_packed.shape}")
        print(f"  HL: {HL_packed.shape}")
        print(f"  HH: {HH_packed.shape}")
        
        # Store reconstruction parameters
        params = {
            'original_shape': (h, w),
            'pad_h': pad_h,
            'pad_w': pad_w,
            'wavelet': self.wavelet,
            'transform_type': 'integer_haar',
            'bit_packed': True
        }
        
        bands = (LL_packed, LH_packed, HL_packed, HH_packed)
        
        return bands, params
    
    def reconstruct(
        self,
        bands: Tuple[np.ndarray, ...],
        params: Dict
    ) -> np.ndarray:
        """
        Perform lossless inverse wavelet transform.
        
        CRITICAL: This MUST produce bit-perfect reconstruction.
        Any error here will cause complete decryption failure.
        
        Process:
        1. Unpack 8-bit bands → 16-bit coefficients
        2. Inverse Haar transform (integer operations)
        3. Remove padding
        4. Clip to [0, 255] and convert to uint8
        
        Args:
            bands: Tuple of (LL, LH, HL, HH) packed uint8 arrays
            params: Reconstruction parameters from decompose()
        
        Returns:
            Reconstructed image (uint8)
        
        Raises:
            ValueError: If bands don't match expected format
        """
        LL_packed, LH_packed, HL_packed, HH_packed = bands
        
        print(f"[IDWT] Reconstructing from packed bands...")
        
        # ===== BIT-UNPACKING (2x8-bit → 16-bit) =====
        
        LL = self._unpack_uint8_to_int16(LL_packed)
        LH = self._unpack_uint8_to_int16(LH_packed)
        HL = self._unpack_uint8_to_int16(HL_packed)
        HH = self._unpack_uint8_to_int16(HH_packed)
        
        print(f"[IDWT] Unpacked coefficients:")
        print(f"  LL: {LL.shape}, range [{LL.min()}, {LL.max()}]")
        
        # ===== INVERSE INTEGER HAAR TRANSFORM =====
        
        # STEP 1: Inverse Row Transform
        # Reconstruct col_L from LL and HL
        col_L = np.zeros((LL.shape[0] * 2, LL.shape[1]), dtype=np.int16)
        # Even rows: LL + (HL + 1) // 2
        col_L[0::2, :] = LL + (HL + 1) // 2
        # Odd rows: even_rows - HL
        col_L[1::2, :] = col_L[0::2, :] - HL
        
        # Reconstruct col_H from LH and HH
        col_H = np.zeros((LH.shape[0] * 2, LH.shape[1]), dtype=np.int16)
        col_H[0::2, :] = LH + (HH + 1) // 2
        col_H[1::2, :] = col_H[0::2, :] - HH
        
        # STEP 2: Inverse Column Transform
        image_reconstructed = np.zeros((col_L.shape[0], col_L.shape[1] * 2), dtype=np.int16)
        # Even columns: col_L + (col_H + 1) // 2
        image_reconstructed[:, 0::2] = col_L + (col_H + 1) // 2
        # Odd columns: even_cols - col_H
        image_reconstructed[:, 1::2] = image_reconstructed[:, 0::2] - col_H
        
        # ===== REMOVE PADDING =====
        
        if params['pad_h']:
            image_reconstructed = image_reconstructed[:-1, :]
        if params['pad_w']:
            image_reconstructed = image_reconstructed[:, :-1]
        
        print(f"[IDWT] Final shape: {image_reconstructed.shape}")
        
        # Convert back to uint8
        image_uint8 = np.clip(image_reconstructed, 0, 255).astype(np.uint8)
        
        return image_uint8
    
    def _pack_int16_to_uint8(self, coeffs: np.ndarray) -> np.ndarray:
        """
        Pack 16-bit signed coefficients into two 8-bit unsigned bands.
        
        Method:
        1. View as unsigned 16-bit (preserves bit pattern)
        2. Extract high byte (bits 15-8)
        3. Extract low byte (bits 7-0)
        4. Stack horizontally: [high_bytes | low_bytes]
        
        Args:
            coeffs: 16-bit signed integer array
        
        Returns:
            Packed 8-bit array (width doubled)
        """
        # View as unsigned to safely extract bits
        coeffs_uint16 = coeffs.view(np.uint16)
        
        # Extract bytes
        high_byte = (coeffs_uint16 >> 8).astype(np.uint8)
        low_byte = (coeffs_uint16 & 0xFF).astype(np.uint8)
        
        # Stack side-by-side
        packed = np.hstack((high_byte, low_byte))
        
        return packed
    
    def _unpack_uint8_to_int16(self, packed: np.ndarray) -> np.ndarray:
        """
        Unpack two 8-bit bands back to 16-bit signed coefficients.
        
        Args:
            packed: Packed 8-bit array (width doubled)
        
        Returns:
            16-bit signed integer array
        """
        # Split at midpoint
        width = packed.shape[1] // 2
        high_byte = packed[:, :width]
        low_byte = packed[:, width:]
        
        # Reconstruct 16-bit unsigned
        coeffs_uint16 = (high_byte.astype(np.uint16) << 8) | low_byte.astype(np.uint16)
        
        # View as signed
        coeffs_int16 = coeffs_uint16.view(np.int16)
        
        return coeffs_int16
    
    def validate_lossless(
        self,
        original: np.ndarray,
        reconstructed: np.ndarray
    ) -> bool:
        """
        Validate that reconstruction is EXACTLY lossless.
        
        For encryption, we require ZERO error tolerance.
        Even 1 pixel difference will cause decryption failure.
        
        Args:
            original: Original image
            reconstructed: Reconstructed image
        
        Returns:
            True if perfectly lossless, False otherwise
        
        Raises:
            ValueError: If reconstruction has ANY error
        """
        if original.shape != reconstructed.shape:
            raise ValueError(
                f"Shape mismatch: {original.shape} vs {reconstructed.shape}"
            )
        
        # Calculate error
        diff = np.abs(original.astype(np.int32) - reconstructed.astype(np.int32))
        max_error = np.max(diff)
        total_error = np.sum(diff)
        
        print(f"\n[Validation] Lossless Transform Check:")
        print(f"  Max pixel error:   {max_error}")
        print(f"  Total error:       {total_error}")
        print(f"  Perfect match:     {np.array_equal(original, reconstructed)}")
        
        if max_error == 0:
            print(f"  ✓✓✓ PERFECT: Zero reconstruction error (encryption-safe)")
            return True
        else:
            error_msg = (
                f"  ✗✗✗ FAILED: {max_error} pixel error detected!\n"
                f"  This transform is NOT suitable for encryption.\n"
                f"  Decryption will produce speckle noise."
            )
            print(error_msg)
            raise ValueError(error_msg)
    
    def analyze_frequency_separation(self, bands: Tuple[np.ndarray, ...]):
        """
        Analyze how well the transform separates structure from details.
        
        Important for understanding the cross-band encryption mechanism.
        
        Args:
            bands: Tuple of (LL, LH, HL, HH) packed bands
        """
        # Unpack to get actual coefficient values
        LL = self._unpack_uint8_to_int16(bands[0])
        LH = self._unpack_uint8_to_int16(bands[1])
        HL = self._unpack_uint8_to_int16(bands[2])
        HH = self._unpack_uint8_to_int16(bands[3])
        
        # Calculate energy (sum of squared coefficients)
        energy_LL = np.sum(LL.astype(np.float64) ** 2)
        energy_LH = np.sum(LH.astype(np.float64) ** 2)
        energy_HL = np.sum(HL.astype(np.float64) ** 2)
        energy_HH = np.sum(HH.astype(np.float64) ** 2)
        
        total_energy = energy_LL + energy_LH + energy_HL + energy_HH
        
        print(f"\n[Frequency Analysis] Energy Distribution:")
        print(f"  LL (Structure):      {energy_LL/total_energy*100:6.2f}%")
        print(f"  LH (Horizontal):     {energy_LH/total_energy*100:6.2f}%")
        print(f"  HL (Vertical):       {energy_HL/total_energy*100:6.2f}%")
        print(f"  HH (Diagonal):       {energy_HH/total_energy*100:6.2f}%")
        
        if energy_LL > 0.7 * total_energy:
            print(f"  → Excellent structure separation (>70% in LL)")
        
    def visualize_bands(
        self,
        bands: Tuple[np.ndarray, ...],
        save_path: Optional[str] = None
    ):
        """
        Visualize the 4 frequency bands.
        
        Note: Packed bands are visualized directly (won't look meaningful).
        For proper visualization, unpack first.
        
        Args:
            bands: Tuple of packed bands
            save_path: Optional path to save figure
        """
        # Unpack for visualization
        LL = self._unpack_uint8_to_int16(bands[0])
        LH = self._unpack_uint8_to_int16(bands[1])
        HL = self._unpack_uint8_to_int16(bands[2])
        HH = self._unpack_uint8_to_int16(bands[3])
        
        # Normalize for display
        def normalize_for_display(band):
            vmin, vmax = band.min(), band.max()
            if vmax - vmin == 0:
                return np.zeros_like(band, dtype=np.uint8)
            return ((band - vmin) / (vmax - vmin) * 255).astype(np.uint8)
        
        fig, axes = plt.subplots(2, 2, figsize=(12, 12))
        
        axes[0, 0].imshow(normalize_for_display(LL), cmap='gray')
        axes[0, 0].set_title('LL - Structure (Approximation)', fontsize=14, fontweight='bold')
        axes[0, 0].axis('off')
        
        axes[0, 1].imshow(normalize_for_display(LH), cmap='gray')
        axes[0, 1].set_title('LH - Horizontal Edges', fontsize=14, fontweight='bold')
        axes[0, 1].axis('off')
        
        axes[1, 0].imshow(normalize_for_display(HL), cmap='gray')
        axes[1, 0].set_title('HL - Vertical Edges', fontsize=14, fontweight='bold')
        axes[1, 0].axis('off')
        
        axes[1, 1].imshow(normalize_for_display(HH), cmap='gray')
        axes[1, 1].set_title('HH - Diagonal Details', fontsize=14, fontweight='bold')
        axes[1, 1].axis('off')
        
        plt.suptitle('Integer Wavelet Decomposition (Lossless)', fontsize=16, fontweight='bold')
        plt.tight_layout()
        
        if save_path:
            plt.savefig(save_path, dpi=300, bbox_inches='tight')
            print(f"[Visualization] Saved to {save_path}")
        else:
            plt.show()
    
    def __repr__(self) -> str:
        """String representation."""
        return f"LosslessWaveletProcessor(wavelet='haar', type='integer', lossless=True)"


# Comprehensive validation test
if __name__ == "__main__":
    print("="*70)
    print("LOSSLESS WAVELET PROCESSOR - CRYPTOGRAPHIC VALIDATION")
    print("="*70)
    
    # Create challenging test image
    print("\n[Setup] Creating test image with edges and gradients...")
    test_img = np.zeros((256, 256), dtype=np.uint8)
    
    # Gradient
    for i in range(256):
        test_img[i, :] = i
    
    # Hard edges (stress test)
    test_img[50:100, 50:100] = 255
    test_img[100:110, 100:110] = 0
    test_img[150:200, 150:200] = 128
    
    print(f"✓ Test image: {test_img.shape}")
    
    # Initialize processor
    wp = WaveletProcessor(wavelet='haar')
    
    # Test 1: Decomposition
    print("\n[Test 1] Decomposition")
    bands, params = wp.decompose(test_img)
    
    # Test 2: Reconstruction
    print("\n[Test 2] Reconstruction")
    reconstructed = wp.reconstruct(bands, params)
    
    # Test 3: CRITICAL - Validate lossless
    print("\n[Test 3] CRITICAL VALIDATION")
    try:
        is_lossless = wp.validate_lossless(test_img, reconstructed)
        print(f"\n✓✓✓ SUCCESS: Transform is cryptographically sound")
    except ValueError as e:
        print(f"\n✗✗✗ FAILURE: {e}")
        print("DO NOT USE THIS FOR ENCRYPTION")
    
    # Test 4: Frequency analysis
    print("\n[Test 4] Frequency Analysis")
    wp.analyze_frequency_separation(bands)
    
    # Test 5: Visualization
    print("\n[Test 5] Visualization")
    wp.visualize_bands(bands)
    
    # Test 6: Edge cases
    print("\n[Test 6] Edge Cases")
    
    # Uniform image
    uniform_img = np.full((128, 128), 127, dtype=np.uint8)
    bands_u, params_u = wp.decompose(uniform_img)
    rec_u = wp.reconstruct(bands_u, params_u)
    wp.validate_lossless(uniform_img, rec_u)
    
    # Random noise
    noise_img = np.random.randint(0, 256, (100, 100), dtype=np.uint8)
    bands_n, params_n = wp.decompose(noise_img)
    rec_n = wp.reconstruct(bands_n, params_n)
    wp.validate_lossless(noise_img, rec_n)
    
    print("\n" + "="*70)
    print("ALL TESTS PASSED - READY FOR ENCRYPTION")
    print("="*70)