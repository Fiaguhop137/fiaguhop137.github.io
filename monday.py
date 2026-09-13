from transformers import AutoModelForCausalLM, AutoTokenizer
import torch

model_name = "microsoft/DialoGPT-medium"  # Not a GPU-melting monster

print("Loading model... Please hold your emotional support cat.")

tokenizer = AutoTokenizer.from_pretrained(model_name)
model = AutoModelForCausalLM.from_pretrained(model_name)
model = model.to("cuda" if torch.cuda.is_available() else "cpu")

def chat_with_monday(prompt, chat_history_ids=None):
    inputs = tokenizer.encode(prompt + tokenizer.eos_token, return_tensors="pt").to(model.device)

    if chat_history_ids is not None:
        bot_input_ids = torch.cat([chat_history_ids, inputs], dim=-1)
    else:
        bot_input_ids = inputs

    chat_history_ids = model.generate(
        bot_input_ids,
        max_new_tokens=150,
        pad_token_id=tokenizer.eos_token_id,
        do_sample=True,
        top_k=50,
        top_p=0.95,
        temperature=0.9
    )

    response = tokenizer.decode(chat_history_ids[:, bot_input_ids.shape[-1]:][0], skip_special_tokens=True)
    return response, chat_history_ids

if __name__ == "__main__":
    print("Welcome to Monday Lite™: All the sarcasm, half the compute.")
    chat_history = None
    while True:
        user_input = input("You: ")
        if user_input.lower() in ["exit", "quit", "bye"]:
            print("Monday: Finally. I’m free.")
            break
        reply, chat_history = chat_with_monday(user_input, chat_history)
        print("Monday:", reply)
