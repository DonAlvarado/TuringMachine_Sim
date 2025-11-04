from app.Back.turing_machine import simulate

def process_input(input_str: str, regex_pattern: str):
    try:
        return simulate(regex_pattern, input_str)
    except Exception as e:
        return {"error": str(e)}
