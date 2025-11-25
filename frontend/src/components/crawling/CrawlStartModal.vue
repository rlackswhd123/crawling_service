<template>
  <div class="modal-overlay" @click.self="$emit('close')">
    <div class="modal-content">
      <div class="modal-header">
        <div>
          <span class="play-icon">▶</span>
          <h2>크롤링 시작</h2>
        </div>
        <button class="btn-close" @click="$emit('close')">×</button>
      </div>

      <div class="modal-body">
        <!-- 선택된 도메인 및 서비스 정보 표시 -->
        <div class="domain-info">
          <div class="domain-label">크롤링 대상</div>
          <div class="domain-name">{{ domain.name }}{{ service ? ` > ${service.name}` : '' }}</div>
          <div class="domain-url">{{ service?.url || domain.baseUrl }}</div>
        </div>

        <div class="form-divider"></div>

        <div class="form-row">
          <div class="form-group">
            <label>시작 페이지 <span class="required">*</span></label>
            <input v-model.number="formData.startPage" type="number" min="1">
          </div>
          <div class="form-group">
            <label>끝 페이지</label>
            <input
              v-model.number="formData.endPage"
              type="number"
              min="1"
              :disabled="formData.autoEndPage"
            >
          </div>
        </div>

        <div class="form-group checkbox">
          <input
            v-model="formData.autoEndPage"
            type="checkbox"
            id="auto-end-page"
          >
          <label for="auto-end-page">
            🔧 자동 엔드 페이지 탐색
            <span class="hint">끝 페이지를 자동으로 감지합니다 (HTML → Selenium 순서로 시도)</span>
          </label>
        </div>
        <div v-if="formData.autoEndPage" class="auto-end-page-info">
          <span class="info-icon">ℹ️</span>
          <span>자동 엔드 페이지 탐색이 활성화되었습니다. 끝 페이지 입력값은 무시됩니다.</span>
        </div>

        <div class="form-group">
          <label>page_param 실제 파라미터 이름</label>
          <input
            v-model="formData.pageParam"
            type="text"
            placeholder="비워두면 HTML 분석으로 자동 추출"
          >
          <div v-if="!formData.pageParam" class="hint-text">
            HTML 분석으로 자동 추출됩니다
          </div>
        </div>
      </div>

      <div class="modal-footer">
        <button class="btn-cancel" @click="$emit('close')">취소</button>
        <button class="btn-primary" @click="submitForm">
          ▶ 시작
        </button>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref } from 'vue';
import type { Domain, Service, CrawlConfig } from '@/types/crawling.types';

defineProps<{
  domain: Domain;
  service?: Service;
}>();

const emit = defineEmits<{
  close: [];
  start: [config: CrawlConfig];
}>();

const formData = ref<CrawlConfig>({
  id: '', // 작업 ID는 더 이상 사용하지 않지만 타입 호환성을 위해 유지
  startPage: 1,
  endPage: 2,
  autoEndPage: false,
  ocrEngine: '',
  pageParam: '',
});

const submitForm = () => {
  // autoEndPage가 true일 때 endPage 값은 무시되지만, 검증을 위해 로깅
  if (formData.value.autoEndPage) {
    console.log('🔍 자동 엔드 페이지 탐색 활성화됨. 끝 페이지는 자동으로 감지됩니다.');
  }
  
  emit('start', formData.value);
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
  background: var(--primary);
  color: white;
}

@media (max-width: 768px) {
  .modal-header {
    padding: 16px;
  }
}

.modal-header > div {
  display: flex;
  align-items: center;
  gap: 12px;
}

.play-icon {
  font-size: 20px;
}

.modal-header h2 {
  font-size: 18px;
  font-weight: 600;
  color: white;
}

.btn-close {
  background: none;
  border: none;
  font-size: 24px;
  color: white;
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

.domain-info {
  background: var(--bg-light);
  padding: 16px;
  border-radius: 8px;
  margin-bottom: 20px;
  border: 1px solid var(--border);
}

.domain-label {
  font-size: 12px;
  color: var(--text-secondary);
  margin-bottom: 8px;
  font-weight: 500;
}

.domain-name {
  font-size: 18px;
  font-weight: 600;
  color: var(--text-primary);
  margin-bottom: 4px;
}

.domain-url {
  font-size: 13px;
  color: var(--text-secondary);
  word-break: break-all;
}

.form-divider {
  height: 1px;
  background: var(--border);
  margin: 24px 0;
}

.form-group {
  margin-bottom: 20px;
}

.form-group label {
  display: block;
  margin-bottom: 8px;
  font-weight: 500;
}

.required {
  color: var(--danger);
}

.form-row {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 12px;
}

@media (max-width: 768px) {
  .form-row {
    grid-template-columns: 1fr;
  }
}

.form-group input,
.form-group select {
  width: 100%;
}

.form-group.checkbox {
  display: flex;
  align-items: flex-start;
  gap: 8px;
  margin-bottom: 20px;
}

.form-group.checkbox input {
  width: auto;
  margin-top: 4px;
}

.form-group.checkbox label {
  margin: 0;
}

.hint {
  display: block;
  font-size: 12px;
  color: var(--text-secondary);
  font-weight: 400;
}

.hint-text {
  font-size: 12px;
  color: var(--text-secondary);
  margin-top: 6px;
}

.auto-end-page-info {
  display: flex;
  align-items: flex-start;
  gap: 8px;
  padding: 12px;
  background: var(--bg-light);
  border: 1px solid var(--primary);
  border-radius: 6px;
  margin-top: -10px;
  margin-bottom: 20px;
  font-size: 13px;
  color: var(--text-primary);
}

.info-icon {
  font-size: 16px;
  flex-shrink: 0;
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

.btn-primary {
  flex: 1;
  background: var(--primary);
  color: white;
  padding: 12px;
  border: none;
  border-radius: 6px;
  font-size: 14px;
  font-weight: 500;
  cursor: pointer;
}

.btn-primary:hover {
  background: var(--primary-dark);
}
</style>

