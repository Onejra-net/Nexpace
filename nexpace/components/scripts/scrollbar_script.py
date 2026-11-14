"""
Dark scrollbar styling.
"""


SCROLLBAR_SCRIPT = """
(function() {
    if (document.getElementById('nexpace-dark-scrollbar')) {
        return;
    }

    const style = document.createElement('style');
    style.id = 'nexpace-dark-scrollbar';

    style.innerHTML = `
        ::-webkit-scrollbar {
            width: 10px !important;
            height: 10px !important;
        }

        ::-webkit-scrollbar-track {
            background: #1e1e1e !important;
        }

        ::-webkit-scrollbar-thumb {
            background: #424242 !important;
            border-radius: 5px !important;
        }

        ::-webkit-scrollbar-thumb:hover {
            background: #4f4f4f !important;
        }
    `;

    if (document.head) {
        document.head.appendChild(style);
    } else {
        document.documentElement.appendChild(style);
    }
})();
"""