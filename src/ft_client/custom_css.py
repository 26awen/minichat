custom_css = """
    :root { 
        --pico-font-size: 100%; 
        --pico-font-family: Pacifico, -apple-system, cursive, 'LXGWWenKaiMono Nerd Font', BlinkMacSystemFont, 'PingFang SC', 'Helvetica Neue', STHeiti, 'Microsoft Yahei', Tahoma, Simsun, sans-serif;
    }
    .modal {
        display: none;
        position: fixed;
        z-index: 1;
        left: 0;
        top: 0;
        width: 100%;
        height: 100%;
        background-color: rgba(0,0,0,0.4);
        justify-content: center;
        align-items: center;
    }
    .modal-content {
        background-color: #fefefe;
        padding: 20px;
        border: 1px solid #888;
        width: 80%;
        max-width: 500px;
        position: relative;
    }
    .close {
        color: #aaa;
        float: right;
        font-size: 28px;
        font-weight: bold;
        cursor: pointer;
    }
    .close:hover,
    .close:focus {
        color: black;
        text-decoration: none;
        cursor: pointer;
    }
    .help-button {
        position: fixed;
        bottom: 12px;
        right: 12px;
        background-color: #4a9eff;
        color: white;
        border: none;
        border-radius: 50%;
        width: 32px;
        height: 32px;
        display: flex;
        align-items: center;
        justify-content: center;
        font-size: 16px;
        box-shadow: 0 2px 4px rgba(0,0,0,0.1);
        transition: all 0.3s ease;
        text-decoration: none;
        animation: pulse 2s infinite;
    }
    .help-button:hover {
        transform: scale(1.1);
        box-shadow: 0 4px 8px rgba(0,0,0,0.2);
        animation: none;
    }
    @keyframes pulse {
        0% {
            transform: scale(1);
            background-color: #4a9eff;
        }
        50% {
            transform: scale(1.05);
            background-color: #3080ff;
        }
        100% {
            transform: scale(1);
            background-color: #4a9eff;
        }
    }
"""