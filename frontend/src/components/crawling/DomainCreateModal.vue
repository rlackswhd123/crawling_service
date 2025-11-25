<template>
  <div class="modal-overlay" @click.self="$emit('close')">
    <div class="modal-content">
      <div class="modal-header">
        <h2>🌐 도메인 추가</h2>
        <button class="btn-close" @click="$emit('close')">×</button>
      </div>

      <div class="modal-body">
        <div class="form-group">
          <label>도메인 이름 <span class="required">*</span></label>
          <input 
            v-model="formData.name" 
            type="text" 
            placeholder="예: NSU 도서관"
            @keyup.enter="submitForm"
          />
        </div>
      </div>

      <div class="modal-footer">
        <button class="btn-cancel" @click="$emit('close')">취소</button>
        <button 
          class="btn-primary" 
          @click="submitForm"
          :disabled="!isFormValid || isSubmitting"
        >
          {{ isSubmitting ? '처리 중...' : '추가' }}
        </button>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, computed } from 'vue';

interface DomainFormData {
  name: string;
}

const emit = defineEmits<{
  close: [];
  create: [domain: DomainFormData];
}>();

const formData = ref({
  name: '',
});

const isSubmitting = ref(false);

const isFormValid = computed(() => {
  return formData.value.name.trim() !== '';
});

const submitForm = () => {
  if (isSubmitting.value) {
    return; // 이미 제출 중이면 무시
  }
  
  if (!isFormValid.value) {
    alert('모든 필수 필드를 채워주세요');
    return;
  }

  isSubmitting.value = true;
  emit('create', {
    name: formData.value.name.trim(),
  });
  
  // 이벤트 발생 후 약간의 지연을 두고 플래그 리셋 (모달이 닫히지 않는 경우 대비)
  setTimeout(() => {
    isSubmitting.value = false;
  }, 1000);
};
</script>

<style scoped>
.modal-content {
  display: flex;
  flex-direction: column;
  max-height: 90vh;
  width: 100%;
  max-width: 500px;
  margin: 0 auto;
}

/* 모바일 반응형 */
@media (max-width: 768px) {
  .modal-content {
    max-width: 100%;
    max-height: 100vh;
    margin: 0;
    border-radius: 0;
  }
}

.modal-header {
  flex-shrink: 0;
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 20px;
  border-bottom: 1px solid var(--border);
  background: white;
}

@media (max-width: 768px) {
  .modal-header {
    padding: 16px;
  }
}

.modal-header h2 {
  font-size: 18px;
  font-weight: 600;
}

.btn-close {
  background: none;
  border: none;
  font-size: 24px;
  color: var(--text-secondary);
  cursor: pointer;
  padding: 0;
  width: 32px;
  height: 32px;
}

.modal-body {
  flex: 1;
  overflow-y: auto;
  padding: 20px;
}

@media (max-width: 768px) {
  .modal-body {
    padding: 16px;
  }
}

.form-group {
  margin-bottom: 20px;
}

.form-group label {
  display: block;
  margin-bottom: 8px;
  font-weight: 500;
  font-size: 14px;
}

.required {
  color: var(--danger);
}

.form-group input {
  width: 100%;
  padding: 10px;
  border: 1px solid var(--border);
  border-radius: 6px;
  font-size: 14px;
}

.form-group input:focus {
  outline: none;
  border-color: var(--primary);
  box-shadow: 0 0 0 2px rgba(99, 102, 241, 0.1);
}

.modal-footer {
  flex-shrink: 0;
  display: flex;
  gap: 12px;
  padding: 20px;
  border-top: 1px solid var(--border);
  background: var(--bg-light);
}

@media (max-width: 768px) {
  .modal-footer {
    padding: 16px;
    flex-direction: column;
  }

  .btn-cancel,
  .btn-primary {
    width: 100%;
  }
}

.btn-cancel {
  flex: 1;
  padding: 12px;
  background: white;
  border: 1px solid var(--border);
  color: var(--text-primary);
  border-radius: 6px;
  font-size: 14px;
  cursor: pointer;
}

.btn-cancel:hover {
  background: var(--bg-light);
}

.btn-primary {
  flex: 1;
  padding: 12px;
  background: var(--primary);
  color: white;
  border: none;
  border-radius: 6px;
  font-size: 14px;
  font-weight: 500;
  cursor: pointer;
}

.btn-primary:hover:not(:disabled) {
  background: var(--primary-dark);
}

.btn-primary:disabled {
  opacity: 0.5;
  cursor: not-allowed;
}
</style>
