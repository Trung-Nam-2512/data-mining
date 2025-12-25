"""
Streamlit Demo Application for Mushroom Classification and Toxicity Detection
"""
import streamlit as st
import torch
from PIL import Image
import numpy as np
from pathlib import Path
import sys

# Add src to path
sys.path.append(str(Path(__file__).parent))

from src.inference import MushroomInference
from src.toxicity import ToxicityClassifier
from src.config import SOURCE_CLASSES, ALL_CLASSES, TOXICITY_MAPPING

# Page configuration
st.set_page_config(
    page_title="Hệ thống Nhận diện Chi Nấm & Cảnh báo Độc tính",
    page_icon="🍄",
    layout="wide"
)

# Custom CSS
st.markdown("""
    <style>
    .main-header {
        font-size: 2.5rem;
        font-weight: bold;
        color: #1f77b4;
        text-align: center;
        margin-bottom: 2rem;
    }
    .warning-box {
        padding: 1rem;
        border-radius: 0.5rem;
        background-color: #ffebee;
        border-left: 5px solid #f44336;
        margin: 1rem 0;
    }
    .safe-box {
        padding: 1rem;
        border-radius: 0.5rem;
        background-color: #e8f5e9;
        border-left: 5px solid #4caf50;
        margin: 1rem 0;
    }
    .prediction-card {
        padding: 1.5rem;
        border-radius: 0.5rem;
        box-shadow: 0 2px 4px rgba(0,0,0,0.1);
        margin: 1rem 0;
    }
    </style>
""", unsafe_allow_html=True)

# Title
st.markdown('<h1 class="main-header">🍄 Hệ thống Nhận diện Chi Nấm & Cảnh báo Độc tính</h1>', unsafe_allow_html=True)

# Sidebar
with st.sidebar:
    st.header("📋 Thông tin hệ thống")
    st.write("""
    **Hệ thống nhận diện chi nấm:**
    - Phase 1: 9 chi từ Source Domain (hiện tại)
    - Phase 2: 11 chi (thêm 2 chi từ Target Domain)
    
    **Tự động cảnh báo độc tính** dựa trên chi nấm được nhận diện.
    """)
    
    st.header("⚠️ Chi nấm độc")
    st.write("""
    - **Amanita**
    - **Cortinarius**
    - **Entoloma**
    - **Inocybe**
    """)
    
    st.header("✅ Chi nấm ăn được")
    st.write("""
    - **Agaricus**
    - **Boletus**
    - **Hygrocybe**
    - **Lactarius**
    - **Russula**
    - **Suillus**
    - **Exidia**
    """)
    
    st.markdown("---")
    st.write("**Lưu ý:** Hệ thống chỉ mang tính chất tham khảo. Không nên dựa hoàn toàn vào kết quả để quyết định ăn nấm hoang dã.")

# Initialize session state
if 'inference_engine' not in st.session_state:
    st.session_state.inference_engine = None
    st.session_state.model_loaded = False

# Model loading section
st.header("🔧 Khởi tạo Model")
col1, col2 = st.columns([3, 1])

with col1:
    model_path = st.text_input(
        "Đường dẫn model (để trống để tự động tìm):",
        value="",
        help="Để trống để tự động tìm model tốt nhất trong thư mục models/"
    )

with col2:
    load_button = st.button("Tải Model", type="primary")

if load_button or st.session_state.model_loaded:
    try:
        if not st.session_state.model_loaded:
            with st.spinner("Đang tải model..."):
                inference_engine = MushroomInference(model_path if model_path else None)
                st.session_state.inference_engine = inference_engine
                st.session_state.model_loaded = True
            st.success("✅ Model đã được tải thành công!")
        else:
            inference_engine = st.session_state.inference_engine
    except Exception as e:
        st.error(f"❌ Lỗi khi tải model: {str(e)}")
        st.info("💡 Hãy đảm bảo bạn đã train model trước bằng lệnh: `python src/train.py`")
        st.session_state.model_loaded = False
        inference_engine = None
else:
    inference_engine = None

# Main prediction section
if st.session_state.model_loaded and inference_engine:
    st.markdown("---")
    st.header("🔍 Nhận diện Chi Nấm")
    
    # File uploader
    uploaded_file = st.file_uploader(
        "Tải lên ảnh nấm để nhận diện",
        type=['jpg', 'jpeg', 'png'],
        help="Hỗ trợ định dạng JPG, JPEG, PNG"
    )
    
    if uploaded_file is not None:
        # Display uploaded image
        col1, col2 = st.columns([1, 1])
        
        with col1:
            image = Image.open(uploaded_file)
            st.image(image, caption="Ảnh đã tải lên", use_container_width=True)
        
        with col2:
            # Predict button
            if st.button("🔍 Nhận diện", type="primary", use_container_width=True):
                # Save uploaded file temporarily
                temp_path = Path("temp_image.jpg")
                image.save(temp_path)
                
                try:
                    # Make prediction
                    with st.spinner("Đang xử lý..."):
                        result = inference_engine.predict(str(temp_path), top_k=3)
                    
                    # Display results
                    st.markdown("### 📊 Kết quả Nhận diện")
                    
                    best_pred = result["best_prediction"]
                    toxicity_info = best_pred["toxicity"]
                    
                    # Toxicity warning box
                    if toxicity_info["is_poisonous"]:
                        st.markdown(f"""
                        <div class="warning-box">
                            <h3>⚠️ {toxicity_info['warning']}</h3>
                            <p><strong>Chi nấm:</strong> {best_pred['genus']}</p>
                            <p><strong>Độc tính:</strong> {toxicity_info['toxicity_description']}</p>
                            <p><strong>Độ tin cậy:</strong> {best_pred['confidence']:.2f}%</p>
                        </div>
                        """, unsafe_allow_html=True)
                    else:
                        st.markdown(f"""
                        <div class="safe-box">
                            <h3>✅ {toxicity_info['warning']}</h3>
                            <p><strong>Chi nấm:</strong> {best_pred['genus']}</p>
                            <p><strong>Độc tính:</strong> {toxicity_info['toxicity_description']}</p>
                            <p><strong>Độ tin cậy:</strong> {best_pred['confidence']:.2f}%</p>
                        </div>
                        """, unsafe_allow_html=True)
                    
                    # Top 3 predictions
                    st.markdown("### 🎯 Top 3 Dự đoán")
                    for pred in result["top_predictions"]:
                        with st.expander(f"{pred['rank']}. {pred['genus']} ({pred['confidence']:.2f}%)"):
                            st.write(f"**Độ tin cậy:** {pred['confidence']:.2f}%")
                            st.write(f"**Độc tính:** {pred['toxicity']['toxicity_description']}")
                            if pred['toxicity']['is_poisonous']:
                                st.warning("⚠️ Chi nấm này có độc tính!")
                            else:
                                st.success("✅ Chi nấm này an toàn để ăn")
                    
                    # All probabilities (optional)
                    with st.expander("📈 Xem tất cả xác suất"):
                        prob_data = result["all_probabilities"]
                        sorted_probs = sorted(prob_data.items(), key=lambda x: x[1], reverse=True)
                        
                        for genus, prob in sorted_probs:
                            toxicity_label = TOXICITY_MAPPING.get(genus, "Unknown")
                            color = "🔴" if toxicity_label == "P" else "🟢"
                            st.write(f"{color} **{genus}:** {prob:.2f}%")
                    
                    # Clean up temp file
                    temp_path.unlink()
                    
                except Exception as e:
                    st.error(f"❌ Lỗi khi nhận diện: {str(e)}")
                    if temp_path.exists():
                        temp_path.unlink()
    
    else:
        st.info("👆 Vui lòng tải lên ảnh nấm để bắt đầu nhận diện")

else:
    st.info("👈 Vui lòng tải model trước khi sử dụng tính năng nhận diện")

# Footer
st.markdown("---")
st.markdown("""
<div style='text-align: center; color: #666; padding: 2rem;'>
    <p>🍄 Hệ thống Nhận diện Chi Nấm & Cảnh báo Độc tính</p>
    <p><small>Data Mining Project - Sử dụng Deep Learning & Transfer Learning</small></p>
    <p><small><strong>Lưu ý:</strong> Hệ thống chỉ mang tính chất tham khảo. Không nên dựa hoàn toàn vào kết quả để quyết định ăn nấm hoang dã.</small></p>
</div>
""", unsafe_allow_html=True)

