"""
AI prompt JavaScript injection helpers.

Responsible for:
- Locating the active chat input field
- Supporting standard and rich-text editors
- Inserting the generated AI prompt
- Dispatching input events to notify web applications
- Reporting the injection result
"""


def build_ai_prompt_injection_script(prompt_json):
    """
    Generate JavaScript for inserting an AI prompt into a web chat.

    Supports standard input fields, contenteditable elements,
    and ProseMirror-based editors.
    """

    # Generate the browser-side prompt injection script:
    return f"""
    (function() {{

        // Identify the currently focused page element.
        let target = document.activeElement;

        // Locate a supported editor if no usable element is focused.
        if (
            !target ||
            target === document.body ||
            target === document.documentElement
        ) {{
            target = document.querySelector(
                'textarea, [contenteditable="true"], div[contenteditable]'
            );
        }}

        // Process the selected input element.
        if (target) {{

            // Handle standard text input fields.
            if (
                target.tagName === 'TEXTAREA' ||
                target.tagName === 'INPUT'
            ) {{
                target.focus();

                // Insert the generated prompt.
                target.value = {prompt_json};

                // Notify the web application of the input change.
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

            // Handle contenteditable and ProseMirror editors.
            }} else if (
                target.getAttribute('contenteditable') === 'true' ||
                target.classList.contains('ProseMirror')
            ) {{
                target.focus();

                // Insert the prompt into the rich-text editor.
                target.innerText = {prompt_json};

                // Notify the editor of the inserted text.
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

            // Report that a target element was found.
            return "SUCCESS";
        }}

        // Report that no target element was found.
        return "NOT_FOUND";
    }})();
    """
