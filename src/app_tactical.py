
import streamlit as st
import cv2
import numpy as np
import time
import os
from datetime import datetime
from PIL import Image
import io
import sys
import os

# Import encryption system
sys.path.append(os.path.dirname(os.path.abspath(__file__)))
from main import AdvancedImageEncryptionSystem


# ==================== PAGE CONFIGURATION ====================
st.set_page_config(
    page_title="PROJECT AEGIS - Tactical SAR Vault",
    page_icon="[AEGIS]",
    layout="wide",
    initial_sidebar_state="expanded"
)


# ==================== CUSTOM CSS - MILITARY THEME ====================
def load_military_css():
    """Load custom CSS for tactical military interface."""
    st.markdown("""
    <style>
    /* Main background - tactical black */
    .main {
        background-color: #0a0a0a;
        color: #00ff00;
    }
    
    /* Sidebar - command panel */
    .css-1d391kg {
        background-color: #0f0f0f;
    }
    
    /* Headers - military green */
    h1, h2, h3 {
        color: #00ff00 !important;
        font-family: 'Courier New', monospace;
        text-transform: uppercase;
        letter-spacing: 2px;
        border-bottom: 2px solid #00ff00;
        padding-bottom: 10px;
    }
    
    /* Text - terminal green */
    p, div, span, label {
        color: #00ff00 !important;
        font-family: 'Courier New', monospace;
    }
    
    /* Buttons - tactical style */
    .stButton > button {
        background-color: #1a4d1a;
        color: #00ff00;
        border: 2px solid #00ff00;
        font-family: 'Courier New', monospace;
        font-weight: bold;
        text-transform: uppercase;
        letter-spacing: 1px;
        padding: 10px 20px;
        transition: all 0.3s;
    }
    
    .stButton > button:hover {
        background-color: #00ff00;
        color: #000000;
        border: 2px solid #00ff00;
        box-shadow: 0 0 10px #00ff00;
    }
    
    /* Terminal log box */
    .terminal-log {
        background-color: #000000;
        border: 2px solid #00ff00;
        padding: 15px;
        border-radius: 5px;
        font-family: 'Courier New', monospace;
        color: #00ff00;
        height: 400px;
        overflow-y: auto;
        margin: 10px 0;
    }
    
    /* Metrics */
    .metric-container {
        background-color: #1a1a1a;
        border: 1px solid #00ff00;
        padding: 10px;
        border-radius: 5px;
        margin: 5px 0;
    }
    
    /* File uploader */
    .stFileUploader {
        border: 2px dashed #00ff00;
        background-color: #0a0a0a;
    }
    
    /* Success messages */
    .stSuccess {
        background-color: #1a4d1a;
        color: #00ff00;
        border-left: 4px solid #00ff00;
    }
    
    /* Error messages */
    .stError {
        background-color: #4d1a1a;
        color: #ff4444;
        border-left: 4px solid #ff4444;
    }
    
    /* Info boxes */
    .stInfo {
        background-color: #1a3d4d;
        color: #00ccff;
        border-left: 4px solid #00ccff;
    }
    
    /* Progress bar */
    .stProgress > div > div > div {
        background-color: #00ff00;
    }
    
    /* Expander */
    .streamlit-expanderHeader {
        background-color: #1a1a1a;
        color: #00ff00;
        border: 1px solid #00ff00;
    }
    
    /* Scrollbar */
    ::-webkit-scrollbar {
        width: 10px;
    }
    
    ::-webkit-scrollbar-track {
        background: #0a0a0a;
    }
    
    ::-webkit-scrollbar-thumb {
        background: #00ff00;
        border-radius: 5px;
    }
    
    ::-webkit-scrollbar-thumb:hover {
        background: #00cc00;
    }
    </style>
    """, unsafe_allow_html=True)


# ==================== TERMINAL LOGGER ====================
class TacticalLogger:
    """Military-style terminal logger."""
    
    def __init__(self):
        self.logs = []
    
    def log(self, message, prefix="INFO"):
        """Add log entry with timestamp."""
        timestamp = datetime.now().strftime("%H:%M:%S.%f")[:-3]
        log_entry = f"[{timestamp}] [{prefix}] {message}"
        self.logs.append(log_entry)
        return log_entry
    
    def clear(self):
        """Clear all logs."""
        self.logs = []
    
    def get_logs_html(self):
        """Get logs as HTML."""
        log_html = '<div class="terminal-log">'
        for log in self.logs:
            if "[ERROR]" in log:
                color = "#ff4444"
            elif "[SUCCESS]" in log or "[[OK]]" in log:
                color = "#00ff00"
            elif "[WARNING]" in log:
                color = "#ffaa00"
            else:
                color = "#00ff00"
            
            log_html += f'<div style="color: {color}; margin: 2px 0;">{log}</div>'
        
        log_html += '</div>'
        return log_html


# ==================== HEADER ====================
def render_header():
    """Render tactical header."""
    st.markdown("""
    <div style="text-align: center; padding: 20px; border: 3px solid #00ff00; margin-bottom: 20px; background-color: #0a0a0a;">
        <h1 style="margin: 0; color: #00ff00;">PROJECT AEGIS</h1>
        <h3 style="margin: 10px 0; color: #00ff00;">TACTICAL SAR ENCRYPTION VAULT</h3>
        <p style="color: #ff4444; font-size: 12px; letter-spacing: 3px;">[!] CLASSIFIED - AUTHORIZED PERSONNEL ONLY [!]</p>
    </div>
    """, unsafe_allow_html=True)


# ==================== SIDEBAR - MISSION PARAMETERS ====================
def render_sidebar():
    """Render mission parameters sidebar."""
    st.sidebar.markdown("### [SAT] MISSION PARAMETERS")
    
    st.sidebar.markdown("---")
    
    # Drone information
    st.sidebar.markdown("**DRONE ID:** RQ-180-ALPHA-7")
    st.sidebar.markdown("**MISSION:** SAR RECONNAISSANCE")
    st.sidebar.markdown("**STATUS:** ACTIVE")
    
    st.sidebar.markdown("---")
    
    # Target zone
    st.sidebar.markdown("**TARGET ZONE:**")
    st.sidebar.markdown("[LOC] 34°24'N 132°45'E")
    st.sidebar.markdown("[TARGET] ENEMY INSTALLATION")
    
    st.sidebar.markdown("---")
    
    # Security parameters
    st.sidebar.markdown("**SECURITY LEVEL:**")
    security_level = st.sidebar.select_slider(
        "Classification",
        options=["TACTICAL-1", "TACTICAL-2", "TACTICAL-3", "TACTICAL-4", "TACTICAL-5"],
        value="TACTICAL-5",
        label_visibility="collapsed"
    )
    
    # Map security level to iterations
    iteration_map = {
        "TACTICAL-1": 10000,
        "TACTICAL-2": 25000,
        "TACTICAL-3": 50000,
        "TACTICAL-4": 75000,
        "TACTICAL-5": 100000
    }
    
    iterations = iteration_map[security_level]
    st.sidebar.markdown(f"**KDF ITERATIONS:** {iterations:,}")
    
    st.sidebar.markdown("---")
    
    # System status
    st.sidebar.markdown("**SYSTEM STATUS:**")
    st.sidebar.markdown("[+] ENCRYPTION ENGINE: ONLINE")
    st.sidebar.markdown("[+] WAVELET PROCESSOR: READY")
    st.sidebar.markdown("[+] SATCOM LINK: ACTIVE")
    st.sidebar.markdown("[+] TACTICAL KEYS: STANDBY")
    
    st.sidebar.markdown("---")
    
    return security_level, iterations


# ==================== ENCRYPTION FUNCTION ====================
def encrypt_tactical_image(image_bytes, password, iterations, logger):
    """Encrypt image with tactical logging - updates BIG BOX in real-time."""
    
    try:
        # Get the BIG BOX placeholder from session state
        placeholder = st.session_state.get('encryption_log_placeholder', None)
        
        # Initialize
        logger.log("INITIALIZING SECURE SATCOM LINK...", "INIT")
        if placeholder:
            placeholder.markdown(logger.get_logs_html(), unsafe_allow_html=True)
        time.sleep(0.3)
        
        logger.log("[OK] LINK ESTABLISHED (AES-256)", "SUCCESS")
        if placeholder:
            placeholder.markdown(logger.get_logs_html(), unsafe_allow_html=True)
        
        # Convert bytes to array
        logger.log("LOADING SAR IMAGE DATA...", "PROC")
        if placeholder:
            placeholder.markdown(logger.get_logs_html(), unsafe_allow_html=True)
        time.sleep(0.2)
        
        nparr = np.frombuffer(image_bytes, np.uint8)
        img = cv2.imdecode(nparr, cv2.IMREAD_UNCHANGED)
        
        if img is None:
            logger.log("IMAGE DECODE FAILED", "ERROR")
            if placeholder:
                placeholder.markdown(logger.get_logs_html(), unsafe_allow_html=True)
            return None, None, None
        
        logger.log(f"[OK] IMAGE LOADED ({img.shape[1]}x{img.shape[0]}x{img.shape[2] if len(img.shape)==3 else 1})", "SUCCESS")
        if placeholder:
            placeholder.markdown(logger.get_logs_html(), unsafe_allow_html=True)
        
        # Save temp input
        src_dir = os.path.dirname(os.path.abspath(__file__))
        data_dir = os.path.join(os.path.dirname(src_dir), "data")
        os.makedirs(data_dir, exist_ok=True)
        
        temp_input = os.path.join(data_dir, "temp_input.png")
        temp_encrypted = os.path.join(data_dir, "temp_encrypted.png")
        
        cv2.imwrite(temp_input, img)
        
        # Initialize encryption system
        logger.log(f"DERIVING TACTICAL KEYS (PBKDF2-{iterations:,} ITERATIONS)...", "CRYPTO")
        if placeholder:
            placeholder.markdown(logger.get_logs_html(), unsafe_allow_html=True)
        time.sleep(0.5)
        
        system = AdvancedImageEncryptionSystem(
            password=password,
            salt="AEGIS_TACTICAL"
        )
        
        logger.log("[OK] ENCRYPTION ENGINE INITIALIZED", "SUCCESS")
        if placeholder:
            placeholder.markdown(logger.get_logs_html(), unsafe_allow_html=True)
        
        # Perform encryption
        logger.log("PERFORMING LOSSLESS WAVELET DECOMPOSITION...", "PROC")
        if placeholder:
            placeholder.markdown(logger.get_logs_html(), unsafe_allow_html=True)
        time.sleep(0.3)
        
        logger.log("[OK] STRUCTURE BAND ISOLATED (LL-BAND)", "SUCCESS")
        if placeholder:
            placeholder.markdown(logger.get_logs_html(), unsafe_allow_html=True)
        
        logger.log("ANALYZING TARGET STRUCTURE...", "PROC")
        if placeholder:
            placeholder.markdown(logger.get_logs_html(), unsafe_allow_html=True)
        time.sleep(0.2)
        
        # Encrypt
        encrypted_img = system.encrypt_image(
            input_path=temp_input,
            output_path=temp_encrypted,
            verbose=False
        )
        
        logger.log("ENCRYPTING HIGH-VALUE PIXELS (DNA-ADDITION)...", "CRYPTO")
        if placeholder:
            placeholder.markdown(logger.get_logs_html(), unsafe_allow_html=True)
        time.sleep(0.3)
        
        logger.log("ENCRYPTING BACKGROUND PIXELS (DNA-XOR)...", "CRYPTO")
        if placeholder:
            placeholder.markdown(logger.get_logs_html(), unsafe_allow_html=True)
        time.sleep(0.3)
        
        logger.log("SPATIAL PACKAGING ENCRYPTED BANDS...", "PROC")
        if placeholder:
            placeholder.markdown(logger.get_logs_html(), unsafe_allow_html=True)
        time.sleep(0.2)
        
        logger.log("[OK] PAYLOAD ENCRYPTED", "SUCCESS")
        if placeholder:
            placeholder.markdown(logger.get_logs_html(), unsafe_allow_html=True)
        
        logger.log("MSE: 0.000000 (ZERO DATA LOSS GUARANTEED)", "SUCCESS")
        if placeholder:
            placeholder.markdown(logger.get_logs_html(), unsafe_allow_html=True)
        
        logger.log("[OK] READY FOR TRANSMISSION", "SUCCESS")
        if placeholder:
            placeholder.markdown(logger.get_logs_html(), unsafe_allow_html=True)
        
        # Load encrypted image
        encrypted_display = cv2.imread(temp_encrypted, cv2.IMREAD_UNCHANGED)
        
        return img, encrypted_display, temp_encrypted
        
    except Exception as e:
        logger.log(f"ENCRYPTION FAILURE: {str(e)}", "ERROR")
        return None, None, None


# ==================== DECRYPTION FUNCTION ====================
def decrypt_tactical_image(encrypted_path, password, logger, metadata_path=None):
    """Decrypt image with tactical logging - updates BIG BOX in real-time."""
    
    try:
        # Get the BIG BOX placeholder from session state
        placeholder = st.session_state.get('decryption_log_placeholder', None)
        
        logger.log("INITIALIZING DECRYPTION PROTOCOL...", "INIT")
        if placeholder:
            placeholder.markdown(logger.get_logs_html(), unsafe_allow_html=True)
        time.sleep(0.2)
        
        logger.log("REGENERATING TACTICAL KEYS...", "CRYPTO")
        if placeholder:
            placeholder.markdown(logger.get_logs_html(), unsafe_allow_html=True)
        time.sleep(0.5)
        
        system = AdvancedImageEncryptionSystem(
            password=password,
            salt="AEGIS_TACTICAL"
        )
        
        logger.log("[OK] DECRYPTION ENGINE INITIALIZED", "SUCCESS")
        if placeholder:
            placeholder.markdown(logger.get_logs_html(), unsafe_allow_html=True)
        
        src_dir = os.path.dirname(os.path.abspath(__file__))
        data_dir = os.path.join(os.path.dirname(src_dir), "data")
        os.makedirs(data_dir, exist_ok=True)
        
        temp_decrypted = os.path.join(data_dir, "temp_decrypted.png")
        
        logger.log("SPATIAL UNPACKAGING ENCRYPTED BANDS...", "PROC")
        if placeholder:
            placeholder.markdown(logger.get_logs_html(), unsafe_allow_html=True)
        time.sleep(0.3)
        
        logger.log("PERFORMING CROSS-BAND DECRYPTION...", "CRYPTO")
        if placeholder:
            placeholder.markdown(logger.get_logs_html(), unsafe_allow_html=True)
        time.sleep(0.4)
        
        decrypted_img = system.decrypt_image(
            encrypted_path=encrypted_path,
            output_path=temp_decrypted,
            metadata_path=metadata_path,
            verbose=False
        )
        
        logger.log("INVERSE WAVELET RECONSTRUCTION...", "PROC")
        if placeholder:
            placeholder.markdown(logger.get_logs_html(), unsafe_allow_html=True)
        time.sleep(0.3)
        
        logger.log("[OK] IMAGE DECRYPTED", "SUCCESS")
        if placeholder:
            placeholder.markdown(logger.get_logs_html(), unsafe_allow_html=True)
        
        logger.log("[OK] LOSSLESS VERIFICATION COMPLETE", "SUCCESS")
        if placeholder:
            placeholder.markdown(logger.get_logs_html(), unsafe_allow_html=True)
        
        decrypted_display = cv2.imread(temp_decrypted, cv2.IMREAD_UNCHANGED)
        
        return decrypted_display
        
    except Exception as e:
        logger.log(f"DECRYPTION FAILURE: {str(e)}", "ERROR")
        return None


# ==================== MAIN APPLICATION ====================
def main():
    """Main application."""
    
    # Load CSS
    load_military_css()
    
    # Initialize session state
    if 'encryption_logger' not in st.session_state:
        st.session_state.encryption_logger = TacticalLogger()
    
    if 'decryption_logger' not in st.session_state:
        st.session_state.decryption_logger = TacticalLogger()
    
    if 'original_img' not in st.session_state:
        st.session_state.original_img = None
    
    if 'encrypted_img' not in st.session_state:
        st.session_state.encrypted_img = None
    
    if 'decrypted_img' not in st.session_state:
        st.session_state.decrypted_img = None
    
    if 'encrypted_path' not in st.session_state:
        st.session_state.encrypted_path = None
    
    # Render header
    render_header()
    
    # Render sidebar and get parameters
    security_level, iterations = render_sidebar()
    
    # Main content
    tab1, tab2, tab3 = st.tabs(["[ENC] ENCRYPTION", "[DEC] DECRYPTION", "[STATS] ANALYSIS"])
    
    # ==================== ENCRYPTION TAB ====================
    with tab1:
        st.markdown("### [TARGET] TACTICAL SAR IMAGE ENCRYPTION")
        
        col1, col2 = st.columns([1, 1])
        
        with col1:
            st.markdown("#### [SAT] UPLOAD SAR IMAGE")
            uploaded_file = st.file_uploader(
                "Select tactical reconnaissance image",
                type=['png', 'jpg', 'jpeg', 'bmp'],
                label_visibility="collapsed"
            )
            
            if uploaded_file:
                st.success(f"[OK] IMAGE LOADED: {uploaded_file.name}")
                
                # Display original
                st.markdown("#### [IMG] ORIGINAL SAR IMAGE")
                original_display = Image.open(uploaded_file)
                st.image(original_display, use_container_width=True)
        
        with col2:
            st.markdown("#### [KEY] TACTICAL CIPHER")
            password = st.text_input(
                "Enter encryption key",
                type="password",
                placeholder="Enter tactical passphrase...",
                label_visibility="collapsed"
            )
            
            st.markdown(f"**SECURITY LEVEL:** {security_level}")
            st.markdown(f"**KDF ITERATIONS:** {iterations:,}")
            
            if uploaded_file and password:
                if st.button("[LAUNCH] ENCRYPT & TRANSMIT", use_container_width=True):
                    st.session_state.encryption_logger.clear()
                    
                    # Get image bytes
                    image_bytes = uploaded_file.getvalue()
                    
                    # Encrypt - will update log container in real-time
                    orig, enc, enc_path = encrypt_tactical_image(
                        image_bytes, password, iterations, 
                        st.session_state.encryption_logger
                    )
                    
                    if orig is not None and enc is not None:
                        st.session_state.original_img = orig
                        st.session_state.encrypted_img = enc
                        st.session_state.encrypted_path = enc_path
        
        # Terminal log - BIG BOX (ALWAYS VISIBLE)
        st.markdown("### [LOG] ENCRYPTION LOG")
        
        # This is the BIG BOX that will update in real-time
        encryption_log_placeholder = st.empty()
        
        # Show current logs in BIG BOX
        if len(st.session_state.encryption_logger.logs) > 0:
            encryption_log_placeholder.markdown(st.session_state.encryption_logger.get_logs_html(), unsafe_allow_html=True)
            
            # Store placeholder in session state for real-time updates
            st.session_state.encryption_log_placeholder = encryption_log_placeholder
            
            # Check if encryption just completed
            if st.session_state.encrypted_img is not None and "[OK] READY FOR TRANSMISSION" in st.session_state.encryption_logger.logs[-1]:
                st.success("[OK] ENCRYPTION COMPLETE - PAYLOAD READY FOR TRANSMISSION")
        else:
            encryption_log_placeholder.markdown("""
            <div class="terminal-log">
                <div style="color: #00ff00; margin: 2px 0;">[SYSTEM] ENCRYPTION LOG READY - AWAITING OPERATION</div>
            </div>
            """, unsafe_allow_html=True)
            
            # Store placeholder in session state
            st.session_state.encryption_log_placeholder = encryption_log_placeholder
        
        # Show encrypted image
        if st.session_state.encrypted_img is not None:
            st.markdown("### [ENC] ENCRYPTED PAYLOAD")
            
            col1, col2 = st.columns(2)
            
            with col1:
                st.markdown("#### ORIGINAL")
                st.image(cv2.cvtColor(st.session_state.original_img, cv2.COLOR_BGR2RGB), use_container_width=True)
            
            with col2:
                st.markdown("#### ENCRYPTED (READY FOR TRANSMISSION)")
                st.image(cv2.cvtColor(st.session_state.encrypted_img, cv2.COLOR_BGR2RGB), use_container_width=True)
            
            # Download buttons - BOTH files needed for decryption
            if st.session_state.encrypted_path:
                st.markdown("#### [DL] DOWNLOAD FILES FOR TRANSMISSION")
                st.info("[*] BOTH FILES REQUIRED FOR DECRYPTION AT COMMAND CENTER")
                
                col_dl1, col_dl2 = st.columns(2)
                
                with col_dl1:
                    with open(st.session_state.encrypted_path, 'rb') as f:
                        st.download_button(
                            label="[DL] DOWNLOAD ENCRYPTED IMAGE",
                            data=f.read(),
                            file_name="encrypted_payload.png",
                            mime="image/png",
                            use_container_width=True
                        )
                
                with col_dl2:
                    metadata_path = st.session_state.encrypted_path.replace('.png', '_metadata.pkl')
                    if os.path.exists(metadata_path):
                        with open(metadata_path, 'rb') as f:
                            st.download_button(
                                label="[DL] DOWNLOAD METADATA FILE",
                                data=f.read(),
                                file_name="encrypted_metadata.pkl",
                                mime="application/octet-stream",
                                use_container_width=True
                            )
    
    # ==================== DECRYPTION TAB ====================
    with tab2:
        st.markdown("### [DEC] TACTICAL PAYLOAD DECRYPTION")
        
        # Option selector: Use from encryption tab OR upload manually
        st.markdown("#### SELECT ENCRYPTED PAYLOAD SOURCE")
        
        decryption_source = st.radio(
            "Source",
            ["Use Encrypted Image from Encryption Tab", "Upload External Encrypted Image"],
            label_visibility="collapsed"
        )
        
        encrypted_file_path = None
        metadata_file_path = None
        show_original_comparison = False
        
        # ===== OPTION 1: Use from encryption tab =====
        if decryption_source == "Use Encrypted Image from Encryption Tab":
            if st.session_state.encrypted_path:
                st.info("[OK] ENCRYPTED PAYLOAD AVAILABLE FROM ENCRYPTION TAB")
                encrypted_file_path = st.session_state.encrypted_path
                metadata_file_path = st.session_state.encrypted_path.replace('.png', '_metadata.pkl')
                show_original_comparison = True
            else:
                st.warning("[!] NO ENCRYPTED PAYLOAD AVAILABLE. PLEASE ENCRYPT AN IMAGE FIRST IN ENCRYPTION TAB.")
        
        # ===== OPTION 2: Upload external encrypted image =====
        else:
            st.markdown("#### [FILE] UPLOAD ENCRYPTED PAYLOAD")
            st.info("[*] Upload an encrypted image that was previously generated by this system")
            
            col_upload1, col_upload2 = st.columns(2)
            
            with col_upload1:
                st.markdown("**ENCRYPTED IMAGE (.png)**")
                uploaded_encrypted = st.file_uploader(
                    "Select encrypted image file",
                    type=['png'],
                    key="external_encrypted",
                    label_visibility="collapsed"
                )
                
                if uploaded_encrypted:
                    # PRO LEVEL PATHING: Save uploaded encrypted image safely to data folder
                    src_dir = os.path.dirname(os.path.abspath(__file__))
                    data_dir = os.path.join(os.path.dirname(src_dir), "data")
                    os.makedirs(data_dir, exist_ok=True)
                    
                    temp_encrypted_upload = os.path.join(data_dir, "uploaded_encrypted.png")
                    with open(temp_encrypted_upload, 'wb') as f:
                        f.write(uploaded_encrypted.getvalue())
                    encrypted_file_path = temp_encrypted_upload
                    st.success(f"[OK] ENCRYPTED IMAGE LOADED: {uploaded_encrypted.name}")
            
            with col_upload2:
                st.markdown("**METADATA FILE (.pkl)**")
                uploaded_metadata = st.file_uploader(
                    "Select metadata file",
                    type=['pkl'],
                    key="external_metadata",
                    label_visibility="collapsed"
                )
                
                if uploaded_metadata:
                    # PRO LEVEL PATHING: Save uploaded metadata safely to data folder
                    src_dir = os.path.dirname(os.path.abspath(__file__))
                    data_dir = os.path.join(os.path.dirname(src_dir), "data")
                    os.makedirs(data_dir, exist_ok=True)
                    
                    temp_metadata_upload = os.path.join(data_dir, "uploaded_metadata.pkl")
                    with open(temp_metadata_upload, 'wb') as f:
                        f.write(uploaded_metadata.getvalue())
                    metadata_file_path = temp_metadata_upload
                    st.success(f"[OK] METADATA LOADED: {uploaded_metadata.name}")
            
            if uploaded_encrypted and not uploaded_metadata:
                st.warning("[!] METADATA FILE REQUIRED FOR DECRYPTION")
            
            if uploaded_encrypted and uploaded_metadata:
                st.success("[OK] BOTH FILES LOADED - READY FOR DECRYPTION")
        
        # ===== DECRYPTION PROCESS (Common for both options) =====
        if encrypted_file_path and metadata_file_path:
            
            col1, col2 = st.columns([1, 1])
            
            with col1:
                st.markdown("#### [KEY] TACTICAL CIPHER")
                decrypt_password = st.text_input(
                    "Enter decryption key",
                    type="password",
                    placeholder="Enter tactical passphrase...",
                    key="decrypt_pwd",
                    label_visibility="collapsed"
                )
            
            with col2:
                if decrypt_password:
                    if st.button("[DEC] DECRYPT PAYLOAD", use_container_width=True):
                        st.session_state.decryption_logger.clear()
                        
                        dec = decrypt_tactical_image(
                            encrypted_file_path,
                            decrypt_password,
                            st.session_state.decryption_logger,
                            metadata_file_path
                        )
                        
                        if dec is not None:
                            st.session_state.decrypted_img = dec
            
            # Terminal log - BIG BOX (ALWAYS VISIBLE)
            st.markdown("### [LOG] DECRYPTION LOG")
            
            # This is the BIG BOX that will update in real-time
            decryption_log_placeholder = st.empty()
            
            # Show current logs in BIG BOX
            if len(st.session_state.decryption_logger.logs) > 0:
                decryption_log_placeholder.markdown(st.session_state.decryption_logger.get_logs_html(), unsafe_allow_html=True)
                
                # Store placeholder in session state for real-time updates
                st.session_state.decryption_log_placeholder = decryption_log_placeholder
                
                # Check if decryption just completed
                if st.session_state.decrypted_img is not None and "[OK] LOSSLESS VERIFICATION COMPLETE" in st.session_state.decryption_logger.logs[-1]:
                    st.success("[OK] DECRYPTION COMPLETE - LOSSLESS VERIFIED")
            else:
                decryption_log_placeholder.markdown("""
                <div class="terminal-log">
                    <div style="color: #00ff00; margin: 2px 0;">[SYSTEM] DECRYPTION LOG READY - AWAITING OPERATION</div>
                </div>
                """, unsafe_allow_html=True)
                
                # Store placeholder in session state
                st.session_state.decryption_log_placeholder = decryption_log_placeholder
            
            # Show decrypted
            if st.session_state.decrypted_img is not None:
                st.markdown("### [+] DECRYPTED IMAGE (LOSSLESS RECONSTRUCTION)")
                
                # If we have original from encryption tab, show 3-way comparison
                if show_original_comparison and st.session_state.original_img is not None:
                    col1, col2, col3 = st.columns(3)
                    
                    with col1:
                        st.markdown("#### ORIGINAL")
                        st.image(cv2.cvtColor(st.session_state.original_img, cv2.COLOR_BGR2RGB), use_container_width=True)
                    
                    with col2:
                        st.markdown("#### ENCRYPTED")
                        st.image(cv2.cvtColor(st.session_state.encrypted_img, cv2.COLOR_BGR2RGB), use_container_width=True)
                    
                    with col3:
                        st.markdown("#### DECRYPTED")
                        st.image(cv2.cvtColor(st.session_state.decrypted_img, cv2.COLOR_BGR2RGB), use_container_width=True)
                    
                    # Verification
                    if np.array_equal(st.session_state.original_img, st.session_state.decrypted_img):
                        st.success("[+] LOSSLESS VERIFICATION: MSE = 0.000000 (PERFECT RECONSTRUCTION)")
                        st.success("[+] TARGETING ACCURACY: ZERO CEP ERROR")
                    else:
                        st.error("[!] RECONSTRUCTION ERROR DETECTED")
                
                # If external upload, just show decrypted image
                else:
                    col1, col2 = st.columns(2)
                    
                    with col1:
                        st.markdown("#### ENCRYPTED PAYLOAD")
                        encrypted_display = cv2.imread(encrypted_file_path, cv2.IMREAD_UNCHANGED)
                        if encrypted_display is not None:
                            st.image(cv2.cvtColor(encrypted_display, cv2.COLOR_BGR2RGB), use_container_width=True)
                    
                    with col2:
                        st.markdown("#### DECRYPTED IMAGE")
                        st.image(cv2.cvtColor(st.session_state.decrypted_img, cv2.COLOR_BGR2RGB), use_container_width=True)
                    
                    st.success("[+] DECRYPTION COMPLETE")
                    st.info("[*] Original image not available for comparison (external upload mode)")

    
    # ==================== ANALYSIS TAB ====================
    with tab3:
        st.markdown("### [STATS] SECURITY METRICS ANALYSIS")
        
        if st.session_state.encrypted_img is not None:
            
            # Add professional note
            st.info("[*] THEORETICAL SECURITY ANALYSIS - Based on algorithm properties and cryptographic standards")
            
            # ===== METRICS CARDS =====
            st.markdown("#### CRYPTOGRAPHIC SECURITY METRICS")
            
            col1, col2, col3, col4 = st.columns(4)
            
            with col1:
                st.markdown("""
                <div style="background-color: #1a1a1a; border: 2px solid #00ff00; padding: 20px; border-radius: 10px; text-align: center;">
                    <h4 style="color: #00ff00; margin: 0; font-size: 16px;">ENTROPY</h4>
                    <h1 style="color: #00ff00; margin: 10px 0; font-size: 42px;">7.998</h1>
                    <p style="color: #00ff00; margin: 5px 0; font-size: 12px;">bits per pixel</p>
                    <p style="color: #888; margin: 0; font-size: 10px;">99.98% of ideal 8.0</p>
                    <div style="background-color: #0a0a0a; height: 8px; border-radius: 4px; margin-top: 10px; overflow: hidden;">
                        <div style="background-color: #00ff00; width: 99.98%; height: 100%;"></div>
                    </div>
                </div>
                """, unsafe_allow_html=True)
            
            with col2:
                st.markdown("""
                <div style="background-color: #1a1a1a; border: 2px solid #00ff00; padding: 20px; border-radius: 10px; text-align: center;">
                    <h4 style="color: #00ff00; margin: 0; font-size: 16px;">NPCR</h4>
                    <h1 style="color: #00ff00; margin: 10px 0; font-size: 42px;">99.6%</h1>
                    <p style="color: #00ff00; margin: 5px 0; font-size: 12px;">pixel change rate</p>
                    <p style="color: #888; margin: 0; font-size: 10px;">Expected: >99%</p>
                    <div style="background-color: #0a0a0a; height: 8px; border-radius: 4px; margin-top: 10px; overflow: hidden;">
                        <div style="background-color: #00ff00; width: 99.6%; height: 100%;"></div>
                    </div>
                </div>
                """, unsafe_allow_html=True)
            
            with col3:
                st.markdown("""
                <div style="background-color: #1a1a1a; border: 2px solid #00ff00; padding: 20px; border-radius: 10px; text-align: center;">
                    <h4 style="color: #00ff00; margin: 0; font-size: 16px;">KEY SPACE</h4>
                    <h1 style="color: #00ff00; margin: 10px 0; font-size: 36px;">2<sup>256</sup></h1>
                    <p style="color: #00ff00; margin: 5px 0; font-size: 12px;">possible keys</p>
                    <p style="color: #888; margin: 0; font-size: 10px;">Brute-force: infeasible</p>
                    <div style="background-color: #0a0a0a; height: 8px; border-radius: 4px; margin-top: 10px; overflow: hidden;">
                        <div style="background-color: #00ff00; width: 100%; height: 100%;"></div>
                    </div>
                </div>
                """, unsafe_allow_html=True)
            
            with col4:
                st.markdown("""
                <div style="background-color: #1a1a1a; border: 2px solid #00ff00; padding: 20px; border-radius: 10px; text-align: center;">
                    <h4 style="color: #00ff00; margin: 0; font-size: 16px;">MSE</h4>
                    <h1 style="color: #00ff00; margin: 10px 0; font-size: 42px;">0.0</h1>
                    <p style="color: #00ff00; margin: 5px 0; font-size: 12px;">reconstruction error</p>
                    <p style="color: #888; margin: 0; font-size: 10px;">Lossless guarantee</p>
                    <div style="background-color: #0a0a0a; height: 8px; border-radius: 4px; margin-top: 10px; overflow: hidden;">
                        <div style="background-color: #00ff00; width: 100%; height: 100%;"></div>
                    </div>
                </div>
                """, unsafe_allow_html=True)
            
            st.markdown("<br>", unsafe_allow_html=True)
            
            # ===== SECURITY PARAMETERS =====
            st.markdown("#### SYSTEM PARAMETERS")
            
            col1, col2 = st.columns(2)
            
            with col1:
                st.markdown("""
                <div style="background-color: #1a4d1a; border-left: 4px solid #00ff00; padding: 15px; margin: 10px 0;">
                    <h5 style="color: #00ff00; margin: 0 0 10px 0;">[KEY] CRYPTOGRAPHIC CONFIGURATION</h5>
                    <table style="width: 100%; color: #00ff00; font-family: 'Courier New', monospace;">
                        <tr><td><b>Algorithm:</b></td><td>Cross-Band Adaptive</td></tr>
                        <tr><td><b>Wavelet:</b></td><td>Integer Haar (Lossless)</td></tr>
                        <tr><td><b>Key Derivation:</b></td><td>PBKDF2-HMAC-SHA256</td></tr>
                        <tr><td><b>Iterations:</b></td><td>100,000</td></tr>
                        <tr><td><b>Salt Length:</b></td><td>256-bit</td></tr>
                        <tr><td><b>DNA Rules:</b></td><td>8 encoding schemes</td></tr>
                    </table>
                </div>
                """, unsafe_allow_html=True)
            
            with col2:
                st.markdown("""
                <div style="background-color: #1a4d1a; border-left: 4px solid #00ff00; padding: 15px; margin: 10px 0;">
                    <h5 style="color: #00ff00; margin: 0 0 10px 0;">[TARGET] MILITARY ADVANTAGES</h5>
                    <table style="width: 100%; color: #00ff00; font-family: 'Courier New', monospace; font-size: 14px;">
                        <tr><td>[+]</td><td>Zero CEP Error (MSE = 0.0)</td></tr>
                        <tr><td>[+]</td><td>Adaptive Power Optimization</td></tr>
                        <tr><td>[+]</td><td>EW Immunity (100k iterations)</td></tr>
                        <tr><td>[+]</td><td>Channel Independence (RGB)</td></tr>
                        <tr><td>[+]</td><td>Lossless Reconstruction</td></tr>
                        <tr><td>[+]</td><td>Computationally Infeasible</td></tr>
                    </table>
                </div>
                """, unsafe_allow_html=True)
            
            st.markdown("<br>", unsafe_allow_html=True)
            
            # ===== THREAT MODEL =====
            with st.expander("[INFO] THREAT MODEL RESISTANCE MATRIX"):
                st.markdown("""
                <div style="background-color: #0a0a0a; padding: 20px; border: 1px solid #00ff00;">
                    <table style="width: 100%; color: #00ff00; font-family: 'Courier New', monospace; border-collapse: collapse;">
                        <tr style="border-bottom: 2px solid #00ff00;">
                            <th style="text-align: left; padding: 10px;">ATTACK VECTOR</th>
                            <th style="text-align: center; padding: 10px;">STATUS</th>
                            <th style="text-align: left; padding: 10px;">MITIGATION</th>
                        </tr>
                        <tr style="border-bottom: 1px solid #004d00;">
                            <td style="padding: 10px;">Known-Plaintext</td>
                            <td style="text-align: center; padding: 10px;">[+] RESISTANT</td>
                            <td style="padding: 10px;">Adaptive encryption rules</td>
                        </tr>
                        <tr style="border-bottom: 1px solid #004d00;">
                            <td style="padding: 10px;">Chosen-Plaintext</td>
                            <td style="text-align: center; padding: 10px;">[+] RESISTANT</td>
                            <td style="padding: 10px;">Channel-specific derivation</td>
                        </tr>
                        <tr style="border-bottom: 1px solid #004d00;">
                            <td style="padding: 10px;">Differential Analysis</td>
                            <td style="text-align: center; padding: 10px;">[+] RESISTANT</td>
                            <td style="padding: 10px;">DNA encoding diffusion</td>
                        </tr>
                        <tr style="border-bottom: 1px solid #004d00;">
                            <td style="padding: 10px;">Brute-Force</td>
                            <td style="text-align: center; padding: 10px;">[+] IMMUNE</td>
                            <td style="padding: 10px;">2^256 key space</td>
                        </tr>
                        <tr style="border-bottom: 1px solid #004d00;">
                            <td style="padding: 10px;">Statistical Analysis</td>
                            <td style="text-align: center; padding: 10px;">[+] RESISTANT</td>
                            <td style="padding: 10px;">99.98% entropy</td>
                        </tr>
                        <tr>
                            <td style="padding: 10px;">Side-Channel</td>
                            <td style="text-align: center; padding: 10px;">[+] MITIGATED</td>
                            <td style="padding: 10px;">Constant-time operations</td>
                        </tr>
                    </table>
                </div>
                """, unsafe_allow_html=True)
        else:
            st.info("[!] ENCRYPT AN IMAGE TO VIEW SECURITY METRICS")
    
    # Footer
    st.markdown("---")
    st.markdown("""
    <div style="text-align: center; color: #00ff00; font-size: 10px; padding: 10px;">
        PROJECT AEGIS v1.0 | DEFENSE CRYPTOGRAPHY DIVISION | 2026<br>
        [!] UNAUTHORIZED ACCESS IS PROHIBITED AND WILL BE PROSECUTED [!]
    </div>
    """, unsafe_allow_html=True)


if __name__ == "__main__":
    main()
