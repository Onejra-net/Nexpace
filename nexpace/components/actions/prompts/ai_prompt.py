"""JavaScript helpers for AI prompt injection."""



def build_ai_prompt_injection_script(prompt_json):
    """Build JavaScript that inserts a prompt into the active chat field.

    The script supports standard text inputs and contenteditable-based
    editors, including ProseMirror.
    """
    
    return f"""
    (function() {{
        let target = document.activeElement;

        if (
            !target ||
            target === document.body ||
            target === document.documentElement
        ) {{
            target = document.querySelector(
                'textarea, [contenteditable="true"], div[contenteditable]'
            );
        }}

        if (target) {{
            if (
                target.tagName === 'TEXTAREA' ||
                target.tagName === 'INPUT'
            ) {{
                target.focus();

                target.value = {prompt_json};

                target.dispatchEvent(
                    new Event(
                        'input',
                        {{ bubbles: true }}
                    )
                );

                target.dispatchEvent(
                    new Event(
                        'change',
                        {{ bubbles: true }}
                    )
                );
            }} else if (
                target.getAttribute('contenteditable') === 'true' ||
                target.classList.contains('ProseMirror')
            ) {{
                target.focus();

                target.innerText = {prompt_json};

                target.dispatchEvent(
                    new InputEvent(
                        'input',
                        {{
                            bubbles: true,
                            inputType: 'insertText',
                            data: {prompt_json}
                        }}
                    )
                );
            }}

            return "SUCCESS";
        }}

        return "NOT_FOUND";
    }})();
    """