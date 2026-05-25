$(document).ready(function() {
    // Автоматическое скрытие flash-сообщений через 5 секунд
    setTimeout(function() {
        $('.alert').fadeOut('slow', function() {
            $(this).remove();
        });
    }, 5000);

    // Функция для показа уведомлений
    window.showNotification = function(message, type) {
        let bgColor = '';
        let icon = '';

        switch(type) {
            case 'success':
                bgColor = 'linear-gradient(135deg, #ff6b8b 0%, #ff4d6d 100%)';
                icon = '🎉';
                break;
            case 'danger':
                bgColor = 'linear-gradient(135deg, #ff9bb0 0%, #ff6b8b 100%)';
                icon = '⚠️';
                break;
            case 'info':
                bgColor = 'linear-gradient(135deg, #ffb8c6 0%, #ff9bb0 100%)';
                icon = '💕';
                break;
            default:
                bgColor = 'linear-gradient(135deg, #ff6b8b 0%, #ff4d6d 100%)';
                icon = '💖';
        }

        const alertDiv = $(`
            <div class="notification-toast" style="position: fixed; top: 80px; right: 20px; z-index: 9999; min-width: 280px; background: ${bgColor}; color: white; padding: 15px 20px; border-radius: 15px; box-shadow: 0 10px 25px rgba(0,0,0,0.2); animation: slideInRight 0.5s ease-out;">
                <div style="display: flex; align-items: center; gap: 10px;">
                    <span style="font-size: 24px;">${icon}</span>
                    <span style="flex: 1;">${message}</span>
                    <button type="button" class="btn-close btn-close-white" onclick="$(this).parent().parent().remove()"></button>
                </div>
            </div>
        `);

        $('body').append(alertDiv);

        setTimeout(function() {
            alertDiv.fadeOut('slow', function() {
                $(this).remove();
            });
        }, 4000);
    };

    // Добавляем анимацию для уведомлений
    const style = document.createElement('style');
    style.textContent = `
        @keyframes slideInRight {
            from {
                opacity: 0;
                transform: translateX(100px);
            }
            to {
                opacity: 1;
                transform: translateX(0);
            }
        }
    `;
    document.head.appendChild(style);
});
