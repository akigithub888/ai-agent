import sys
import os
from google import genai
from google.genai import types
from dotenv import load_dotenv
from functions.get_files_info import schema_get_files_info
from functions.get_file_content import schema_get_file_content
from functions.run_python import schema_run_python_file
from functions.write_file_content import schema_write_file
from functions.call_function import call_function
system_prompt = system_prompt = """
You are a helpful AI coding agent.

When a user asks a question or makes a request, make a function call plan. You can perform the following operations:

- List files and directories
- Read file contents
- Execute Python files with optional arguments
- Write or overwrite files

All paths you provide should be relative to the working directory. You do not need to specify the working directory in your function calls as it is automatically injected for security reasons.
Complete all necessary function calls before providing your final answer. Do not explain your plan - just execute it.
"""


available_functions = types.Tool(
    function_declarations=[
        schema_get_files_info,
        schema_get_file_content,
        schema_run_python_file,
        schema_write_file,
    ]
)

def main():
    load_dotenv()

    verbose = "--verbose" in sys.argv
    args = []
    for arg in sys.argv[1:]:
        if not arg.startswith("--"):
            args.append(arg)

    if not args:
        print("AI Code Assistant")
        print('\nUsage: python main.py "your prompt here" [--verbose]')
        print('Example: python main.py "How do I build a calculator app?"')
        sys.exit(1)


    api_key = os.environ.get("GEMINI_API_KEY")
    client = genai.Client(api_key=api_key)

    user_prompt = " ".join(args)

    if verbose:
        print(f"User prompt: {user_prompt}\n")

    messages = [
        types.Content(role="user", parts=[types.Part(text=user_prompt)]),
    ]

    for i in range(20):
        try:
            response, messages = generate_content(client, messages, verbose)
            final_text = response.text.strip() if response.text else ""
            if final_text and len(final_text) > 2:  # length > 2 avoids things like '.' or '\n'
                print("Final response:")
                print(final_text)
                break
        except Exception as e:
            print(f"Error:{e}")
            break
    
def generate_content(client, messages, verbose):
    response = client.models.generate_content(
        model="gemini-2.0-flash-001",
        contents=messages,
        config=types.GenerateContentConfig(tools=[available_functions], system_instruction=system_prompt),
    )
    if verbose:
        print("Prompt tokens:", response.usage_metadata.prompt_token_count)
        print("Response tokens:", response.usage_metadata.candidates_token_count)
    # print("Response:")
    for candidate in response.candidates:
        messages.append(candidate.content)
    if response.function_calls:
        for call in response.function_calls:
            result = call_function(call, verbose)
            func_response = types.Content(role="model", parts=[types.Part(text=f"Tool response: \n{result.parts[0].function_response.response['result']}")])
            messages.append(func_response)  # This appends the Content object directly
            if not result.parts[0].function_response.response:
                raise Exception("This is a fatal error")
            if verbose:
                print(f"-> {result.parts[0].function_response.response}")
    return response, messages

if __name__ == "__main__":
    main()
