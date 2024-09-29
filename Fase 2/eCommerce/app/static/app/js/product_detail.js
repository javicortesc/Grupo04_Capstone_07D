document.addEventListener('DOMContentLoaded', () => {
    const viewDetailButton = document.querySelectorAll('.view-detail-btn');
    
    viewDetailButton.forEach(button => {
      button.addEventListener('click', () => {
        const productId = button.getAttribute('data-product-id');
        window.location.href = `/product-detail/${productId}/`;
      });
    });
  });