document.addEventListener('DOMContentLoaded', function() {
  const hiddenFields = document.getElementById('hidden-fields');
  const productInput = document.getElementById('itemName');
  const skuInput = document.getElementById('sku');
  const descInput = document.getElementById('description');
  const categoryInput = document.getElementById('category');
  const quantityInput = document.getElementById('quantity');
  const unitInput = document.getElementById('unit');
  const locationInput = document.getElementById('location');
  const minStockInput = document.getElementById('minStock');

  let debounceTimer;

  function checkProduct(searchType, searchValue) {
    clearTimeout(debounceTimer);

    if (!searchValue) {
      hiddenFields.style.display = 'none';
      return;
    }

    debounceTimer = setTimeout(function() {
      const requestBody = searchType === 'name'
        ? { product_name: searchValue }
        : { sku: searchValue };

      fetch('/api/check-product', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify(requestBody),
      })
      .then(response => response.json())
      .then(data => {
        if (data.exists) {
          hiddenFields.style.display = 'block';

          const product = data.product;

          if (searchType !== 'name' && productInput) productInput.value = product.productName || '';
          if (searchType !== 'sku' && skuInput) skuInput.value = product.productCode || '';

          if (descInput) descInput.value = product.productDescription || '';
          if (categoryInput) categoryInput.value = product.category || '';
          if (quantityInput) quantityInput.value = product.quantityInStock || '';
          if (unitInput) unitInput.value = product.unit || '';
          if (locationInput) locationInput.value = product.location || '';
          if (minStockInput) minStockInput.value = product.minimalQuantity || '';

        } else {
          hiddenFields.style.display = 'none';

          if (descInput) descInput.value = '';
          if (categoryInput) categoryInput.value = '';
          if (quantityInput) quantityInput.value = '';
          if (unitInput) unitInput.value = '';
          if (locationInput) locationInput.value = '';
          if (minStockInput) minStockInput.value = '';
        }
      })
      .catch(error => {
        console.error('Error checking product:', error);
      });
    }, 300);
  }

  productInput.addEventListener('input', function() {
    checkProduct('name', this.value.trim());
  });

  skuInput.addEventListener('input', function() {
    checkProduct('sku', this.value.trim());
  });
});
