import React from 'react';
import './Modal.css';

function DeleteModal({ onConfirm, onCancel }) {
  return (
    <div className="modal-backdrop">
      <div className="modal">
        <p>정말 삭제하시겠어요?</p>
        <div className="modal-buttons">
          <button className="confirm" onClick={onConfirm}>삭제</button>
          <button className="cancel" onClick={onCancel}>취소</button>
        </div>
      </div>
    </div>
  );
}

export default DeleteModal;