function confirmDelete(entity) {
    return window.confirm(`Deseja excluir este ${entity.toLowerCase()}? Se ele já estiver relacionado, será apenas inativado para preservar o histórico.`);
}

function formatMoney(value) {
    return Number(value || 0).toLocaleString('pt-BR', { style: 'currency', currency: 'BRL' });
}

document.addEventListener('DOMContentLoaded', () => {
    document.querySelectorAll('.feature-card input[type="checkbox"]').forEach(input => {
        const card = input.closest('.feature-card');
        const status = card?.querySelector('.feature-card-status');
        if (!card) return;

        const refreshFeatureCard = () => {
            card.classList.toggle('enabled', input.checked);
            if (status) status.textContent = input.checked ? 'Visível' : 'Oculta';
        };

        input.addEventListener('change', refreshFeatureCard);
        refreshFeatureCard();
    });
});

document.addEventListener('DOMContentLoaded', () => {
    const itemsContainer = document.querySelector('#order-items');
    const addItemButton = document.querySelector('#add-item');
    const totalElement = document.querySelector('#order-total');
    const productTemplate = document.querySelector('#product-options');

    if (!itemsContainer || !addItemButton || !productTemplate) return;

    const optionsMarkup = productTemplate.innerHTML;

    function updateTotal() {
        let total = 0;
        itemsContainer.querySelectorAll('.order-item-row').forEach(row => {
            const product = row.querySelector('.product-select');
            const quantity = row.querySelector('.quantity-input');
            const selected = product?.selectedOptions[0];
            const price = Number(selected?.dataset.price || 0);
            const qty = Number(quantity?.value || 0);
            const subtotal = price * qty;
            total += subtotal;
            const subtotalElement = row.querySelector('.item-subtotal');
            if (subtotalElement) subtotalElement.textContent = formatMoney(subtotal);
        });
        if (totalElement) totalElement.textContent = formatMoney(total);
    }

    function addItemRow() {
        const row = document.createElement('div');
        row.className = 'order-item-row';
        row.innerHTML = `
            <label class="field product-field"><span>Produto</span><select class="product-select" name="produto_id[]" required><option value="">Selecione...</option>${optionsMarkup}</select></label>
            <label class="field quantity-field"><span>Quantidade</span><input class="quantity-input" type="number" name="quantidade[]" value="1" min="1" required></label>
            <div class="item-total"><small>Subtotal</small><strong class="item-subtotal">R$ 0,00</strong></div>
            <button class="icon-button delete remove-item" type="button" title="Remover produto" aria-label="Remover produto"><span class="material-symbols-outlined">delete</span></button>
        `;
        itemsContainer.appendChild(row);
        row.querySelector('.product-select').addEventListener('change', updateTotal);
        row.querySelector('.quantity-input').addEventListener('input', updateTotal);
        row.querySelector('.remove-item').addEventListener('click', () => {
            row.remove();
            updateTotal();
        });
        updateTotal();
    }

    addItemButton.addEventListener('click', addItemRow);
    addItemRow();
});
