<template>
  <div class="modal-overlay" @click.self="$emit('close')">
    <div class="modal-content">
      <div class="modal-header">
        <h2>태그/셀렉터 확인</h2>
        <button class="btn-close" @click="$emit('close')">×</button>
      </div>

      <div class="modal-body">
        <div class="form-group">
          <label>현재 셀렉터</label>
          <textarea
            v-model="currentSelector"
            readonly
            rows="3"
            class="selector-display"
          ></textarea>
        </div>

        <div class="preview-section">
          <h3>미리보기</h3>
          <div class="preview-text">
            {{ previewText }}
          </div>
        </div>

        <div class="form-group">
          <label>셀렉터 수정</label>
          <input v-model="newSelector" type="text" placeholder="CSS selector">
          <button class="btn-update" @click="updateSelector">적용</button>
        </div>

        <button class="btn-confirm" @click="confirmTag">
          ✓ 이 태그가 맞습니다
        </button>
      </div>

      <div class="modal-footer">
        <button class="btn-cancel" @click="$emit('close')">닫기</button>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref } from 'vue';
import type { Post } from '@/types/crawling.types';

const props = defineProps<{
  post: Post;
}>();

const emit = defineEmits<{
  close: [];
}>();

const currentSelector = ref(props.post?.selector || '');
const newSelector = ref('');
const previewText = ref(props.post?.content?.substring(0, 200) + '...' || '');

const updateSelector = () => {
  if (newSelector.value) {
    currentSelector.value = newSelector.value;
    // 실제 본문 내용 표시
    previewText.value = props.post?.content?.substring(0, 200) + '...' || '';
    newSelector.value = '';
  }
};

const confirmTag = () => {
  console.log('[v0] Tag confirmed with selector:', currentSelector.value);
  emit('close');
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
  margin: 0;
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
  font-size: 13px;
}

.selector-display {
  width: 100%;
  background: var(--bg-light);
  border: 1px solid var(--border);
  padding: 12px;
  border-radius: 6px;
  font-family: 'Monaco', 'Courier New', monospace;
  font-size: 12px;
  resize: none;
}

.preview-section {
  background: var(--bg-light);
  padding: 12px;
  border-radius: 6px;
  margin-bottom: 20px;
}

.preview-section h3 {
  font-size: 13px;
  font-weight: 600;
  margin-bottom: 8px;
}

.preview-text {
  font-size: 12px;
  line-height: 1.6;
  color: var(--text-secondary);
}

.form-group input {
  width: 100%;
  margin-bottom: 8px;
}

.btn-update {
  background: var(--bg-light);
  border: 1px solid var(--border);
  color: var(--text-primary);
  width: 100%;
}

.btn-update:hover {
  background: var(--border);
}

.btn-confirm {
  width: 100%;
  background: var(--primary);
  color: white;
  margin-bottom: 20px;
}

.btn-confirm:hover {
  background: var(--primary-dark);
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
  }
}

.btn-cancel {
  width: 100%;
  background: white;
  border: 1px solid var(--border);
  color: var(--text-primary);
  padding: 12px;
  border-radius: 6px;
  font-size: 14px;
  cursor: pointer;
}

.btn-cancel:hover {
  background: var(--bg-light);
}

@media (max-width: 768px) {
  .btn-update,
  .btn-confirm {
    width: 100%;
    padding: 12px;
    border-radius: 6px;
    font-size: 14px;
    border: none;
    cursor: pointer;
    margin-bottom: 12px;
  }
}
</style>

