import time
import requests
from PIL import Image,ImageEnhance, ImageFilter
from io import BytesIO
from config import HF_API_KEY

MODELS = [
    "ByteDance/SDXL-Lightning",
    "black-forest-labs/FLUX.1-dev",
    "stabilityai/stable-diffusion-xl-base-1.0",
]
HEADERS = {"Authorization": f"Bearer {HF_API_KEY}", "Accept": "image/png"}

def generate_image_from_text(prompt):
    payload={"inputs": prompt}
    last_error = None
    for model in MODELS:
        url=f"https://router.huggingface.co/hf-interference/models/{model}"
        for _ in range(3):
                r=requests.post(url,headers=HEADERS,json=payload,timeout=120)
                ct=(r.headers.get("content-type") or "").lower()
                if r.status_code==503 and "application/json" in ct:
                    try:
                        wait_s=int(r.json().get("estimated_time", 5))
                    except Exception:
                        wait_s=5
                    time.sleep(wait_s+1)
                    continue
                if r.status_code==200 and "application/json" not in ct:
                    try:
                         return Image.open(BytesIO(r.content)).convert("RGB")
                    except Exception as e:
                         last_err=f"Request failed with status code 200: could not decode image {e}"
                         break

                try:
                     body=r.json() if "application/json" in ct else r.text
                    except Exception:
                        body=r.text
                    last_err=f"request failed with status code {r.status_code}: {body}"
                break

        raise Exception(last_err or "Request failed with status code 500: unknown error")
    def post_process_image(image):
        image=ImageEnhance.brightness(image).enhance(1.2)
        image=ImageEnhance.Contrast(image).enhance(1.2)
        return image.filter(ImageFilter.GaussianBlur(radius=2))

def main():
     print("welcome to post processing magic workshop")
     print("type exit to quit")
     while True:
          user_input=input("enter a description for the image or type exit ")
          if user_input.lower()=="exit":
               print("bye bye")
               break
          try:
               print("generating image...")
               image=generate_image_from_text(user_input)
               print("Applying post processing effects")
               processed_image=post_process_image(image)
               processed_image.show()

               save_option=input("do you want to save the image (yes/no)").strip().lower()
               if save_option=="yes":
                    filename=input("enter name of the file").strip()
                    processed_image.save(f"{filename}.png")
                    print("saved file")
            except Exception as e:
                print("An error occured",e )

if __name__=="__main__":
    main()