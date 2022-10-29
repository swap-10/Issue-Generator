import gradio as gr
import tensorflow as tf
from transformers import AutoTokenizer

def sample_top_k(logits, top_k):

  top_k = tf.clip_by_value(
      top_k, clip_value_min=1, clip_value_max=tf.shape(logits)[-1])
  top_k_logits = tf.math.top_k(logits, k=top_k)
  return top_k_logits.indices.numpy()


model = tf.saved_model.load('saved_model/issues_model')
infer = model.signatures["serving_default"]
tokenizer = AutoTokenizer.from_pretrained('gpt2')
tokenizer.pad_token_id = tokenizer.eos_token_id

def generate_issues(input):
    final_output = ""
    for i in range(10):
        tokenized_input = tokenizer(input, return_tensors='tf')
        print("Tokenized input: ")
        print(tokenized_input)
        print("Outputs:\n\n\n")
        outputs = infer(input_ids=tf.constant(tokenized_input['input_ids'].numpy().astype('int64')), attention_mask=tf.constant(tokenized_input['attention_mask'].numpy().astype('int64')))['logits']
        print(f"{outputs}\nShape: {outputs.shape}")
        outputs = tf.squeeze(outputs)
        top_k_outputs_indices = sample_top_k(outputs, top_k=16)
        if len(top_k_outputs_indices.shape) == 1:
            top_k_outputs_indices = tf.expand_dims(top_k_outputs_indices, axis=0)
        random_indices = tf.random.uniform(minval=0, maxval=16, dtype='int32', shape=[1]).numpy()
        outputs = tokenizer.decode(top_k_outputs_indices[:, random_indices[0]])
        
        final_output += " " + outputs.split()[-1]
        input += " " + outputs.split()[-1]
    return final_output

iface = gr.Interface(fn=generate_issues, inputs="text", outputs="text")
iface.launch()