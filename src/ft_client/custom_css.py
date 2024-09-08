custom_css = """
    :root { 
        --pico-font-size: 100%; 
        --pico-font-family: 'Microsoft Yahei', Pacifico, -apple-system, cursive, 'LXGWWenKaiMono Nerd Font', BlinkMacSystemFont, 'PingFang SC', 'Helvetica Neue', STHeiti, Tahoma, Simsun, sans-serif;
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

custom_css += """
.dropdown {
    position: relative;
    display: inline-block;
}

.dropbtn {
    background-color: #24292e;
    color: white;
    padding: 10px 20px;
    font-size: 16px;
    border: none;
    cursor: pointer;
    border-radius: 4px;
    width: 120px;
    text-align: center;
}

.dropdown-content {
    display: none;
    position: absolute;
    right: 0;
    background-color: #f9f9f9;
    min-width: 120px;
    box-shadow: 0px 8px 16px 0px rgba(0,0,0,0.2);
    z-index: 1;
    border-radius: 4px;
}

.dropdown-content a {
    color: white;
    padding: 12px 16px;
    text-decoration: none;
    display: block;
    text-align: center;
}

.login-option {
    width: 100%;
    box-sizing: border-box;
}

.login-option.github {
    background-color: #24292e;
}

.login-option.google {
    background-color: #4285F4;
}

.dropdown-content a:hover {
    opacity: 0.8;
}

.dropdown:hover .dropdown-content {
    display: block;
}

.dropdown:hover .dropbtn {
    opacity: 0.8;
}
"""