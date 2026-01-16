import torch
from diffusers import DiffusionPipeline
import gradio as gr

# --- Model Loading (with Memory Optimization) ---
print("Loading Mission Control Systems...")
base = DiffusionPipeline.from_pretrained(
    "stabilityai/stable-diffusion-xl-base-1.0",
    torch_dtype=torch.float16,
    variant="fp16",
    use_safetensors=True,
)
base.enable_model_cpu_offload()

refiner = DiffusionPipeline.from_pretrained(
    "stabilityai/stable-diffusion-xl-refiner-1.0",
    text_encoder_2=base.text_encoder_2,
    vae=base.vae,
    torch_dtype=torch.float16,
    use_safetensors=True,
    variant="fp16",
)
refiner.enable_model_cpu_offload()

# --- Generation Logic ---
def generate_image(prompt, negative_prompt, style_preset, num_steps, guidance_scale):
    # Apply Style Presets
    if style_preset == "Cyberpunk":
        prompt = f"{prompt}, cyberpunk, neon lights, high tech, futuristic, detailed, 8k"
        negative_prompt = f"{negative_prompt}, vintage, rustic, dull, low resolution"
    elif style_preset == "Synthwave":
        prompt = f"{prompt}, synthwave, retrowave, purple and pink grid, 80s aesthetics"
    elif style_preset == "Bio-Tech":
        prompt = f"{prompt}, organic technology, biomechanical, hr giger style, sleek white"
    
    # Run Base
    image = base(
        prompt=prompt,
        negative_prompt=negative_prompt,
        num_inference_steps=num_steps,
        guidance_scale=guidance_scale,
        denoising_end=0.8,
        output_type="latent",
    ).images
    
    # Run Refiner
    image = refiner(
        prompt=prompt,
        negative_prompt=negative_prompt,
        num_inference_steps=num_steps,
        denoising_start=0.8,
        image=image,
    ).images[0]
    
    return image

# --- Futuristic UI ---
theme = gr.themes.Soft(
    primary_hue="cyan",
    neutral_hue="slate",
    font=[gr.themes.GoogleFont("Orbitron"), "sans-serif"]
).set(
    body_background_fill="#0b0f19",
    body_text_color="#ccd6f6",
    block_background_fill="#112240",
    block_label_text_color="#64ffda",
    button_primary_background_fill="#64ffda",
    button_primary_text_color="#0b0f19"
)

with gr.Blocks(theme=theme, title="AI Mission Control") as app:
    with gr.Row():
        gr.Markdown("# 🚀 AI IMAGINATION ENGINE // TERMINAL 01")
    
    with gr.Row():
        with gr.Column(scale=1):
            prompt = gr.Textbox(label="COMMAND PROMPT", placeholder="Enter visual coordinates...", lines=3)
            negative_prompt = gr.Textbox(label="EXCLUSION PARAMETERS", placeholder="What to avoid...", value="blurry, low quality, ugly, deformed")
            
            with gr.Accordion("ADVANCED TELEMETRY", open=True):
                style = gr.Radio(["Raw", "Cyberpunk", "Synthwave", "Bio-Tech"], label="AESTHETIC MODULE", value="Cyberpunk")
                steps = gr.Slider(minimum=10, maximum=100, value=40, step=1, label="COMPUTE CYCLES (Steps)")
                guidance = gr.Slider(minimum=1.0, maximum=20.0, value=7.5, step=0.5, label=" adherence FACTOR (Guidance)")
            
            btn = gr.Button("INITIATE GENERATION", size="lg")
        
        with gr.Column(scale=2):
            output = gr.Image(label="VISUAL OUTPUT")
            
    btn.click(fn=generate_image, inputs=[prompt, negative_prompt, style, steps, guidance], outputs=output)

if __name__ == "__main__":
    app.launch()
