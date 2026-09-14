document.addEventListener('DOMContentLoaded', () => {
    const board = document.querySelector('[data-board]');
    const itemDialog = document.querySelector('#board-item-dialog');
    const itemForm = document.querySelector('#board-item-form');
    const deleteDialog = document.querySelector('#board-delete-dialog');
    const deleteForm = document.querySelector('#board-delete-form');

    if (!board) return;

    let draggedCard = null;
    const createAction = itemForm?.getAttribute('action') || '';

    function openDialog(dialog) {
        if (dialog && !dialog.open) dialog.showModal();
    }

    function closeDialog(dialog) {
        if (dialog?.open) dialog.close();
    }

    function resetItemForm() {
        if (!itemForm) return;
        itemForm.action = createAction;
        itemForm.reset();
        document.querySelector('#board-dialog-title').textContent = 'Nova demanda';
        document.querySelector('#board-item-status').value = 'NAO_INICIADO';
    }

    document.querySelectorAll('[data-open-board-modal]').forEach(button => {
        button.addEventListener('click', () => {
            resetItemForm();
            openDialog(itemDialog);
        });
    });

    document.querySelectorAll('[data-close-dialog]').forEach(button => {
        button.addEventListener('click', () => closeDialog(button.closest('dialog')));
    });

    document.querySelectorAll('[data-open-delete]').forEach(button => {
        button.addEventListener('click', () => {
            if (!deleteForm || !deleteDialog) return;
            deleteForm.action = `/board/items/${button.dataset.itemId}/excluir`;
            document.querySelector('#board-delete-item-title').textContent = `“${button.dataset.itemTitle}”`;
            openDialog(deleteDialog);
        });
    });

    document.querySelectorAll('[data-board-card]').forEach(card => {
        if (card.dataset.editable === 'true') {
            card.addEventListener('dblclick', () => {
                if (!itemForm || !itemDialog) return;
                itemForm.action = `/board/items/${card.dataset.itemId}`;
                document.querySelector('#board-dialog-title').textContent = 'Editar demanda';
                document.querySelector('#board-item-title').value = card.dataset.title || '';
                document.querySelector('#board-item-description').value = card.dataset.description || '';
                document.querySelector('#board-item-status').value = card.dataset.status || 'NAO_INICIADO';
                openDialog(itemDialog);
            });
        }

        card.addEventListener('dragstart', event => {
            if (card.getAttribute('draggable') !== 'true') {
                event.preventDefault();
                return;
            }
            draggedCard = card;
            card.classList.add('is-dragging');
            event.dataTransfer.effectAllowed = 'move';
            event.dataTransfer.setData('text/plain', card.dataset.itemId || '');
        });

        card.addEventListener('dragend', () => {
            card.classList.remove('is-dragging');
            draggedCard = null;
            document.querySelectorAll('[data-board-column]').forEach(column => column.classList.remove('is-drop-target'));
        });
    });

    document.querySelectorAll('[data-board-column]').forEach(column => {
        column.addEventListener('dragover', event => {
            if (!draggedCard) return;
            event.preventDefault();
            column.classList.add('is-drop-target');
        });

        column.addEventListener('dragleave', event => {
            if (event.target === column || !column.contains(event.relatedTarget)) {
                column.classList.remove('is-drop-target');
            }
        });

        column.addEventListener('drop', async event => {
            event.preventDefault();
            column.classList.remove('is-drop-target');
            if (!draggedCard) return;

            const status = column.dataset.status;
            const itemId = draggedCard.dataset.itemId;
            const previousColumn = draggedCard.closest('[data-board-column]');
            if (!status || !itemId || previousColumn?.dataset.status === status) return;

            column.querySelector('.board-column-body')?.appendChild(draggedCard);
            try {
                const response = await fetch(`/board/items/${itemId}/status`, {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json', 'Accept': 'application/json' },
                    body: JSON.stringify({ status })
                });
                const result = await response.json().catch(() => ({}));
                if (!response.ok || !result.ok) {
                    throw new Error(result.error || 'Não foi possível atualizar o status.');
                }
                window.location.reload();
            } catch (error) {
                window.alert(error.message);
                window.location.reload();
            }
        });
    });
});
