from gpt4all import GPT4All

# Replace with the exact filename of your .bin model
MODEL_PATH = "ggml-gpt4all-j-v1.3-groovy.bin"

def main():
    # Initialize the GPT4All model
    gptj = GPT4All(model=MODEL_PATH)
    
    # Generate text
    prompt = "You are a hype coach. The player just got a triple kill in an FPS game. Respond with one short line."
    response = gptj.generate(
        prompt,
        max_tokens=50,    # adjust as needed
        temperature=0.9,  # creativity
    )
    print("Model Response:", response)

if __name__ == "__main__":
    main()

