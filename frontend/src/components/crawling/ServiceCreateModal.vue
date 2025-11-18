<template>
  <div class="modal-overlay" @click.self="$emit('close')">
    <div class="modal-content">
      <div class="modal-header">
        <h2>📋 게시판 추가</h2>
        <button class="btn-close" @click="$emit('close')">×</button>
      </div>

      <div class="modal-body">
        <!-- Step 1: 기본 정보 입력 -->
        <div class="step-section">
          <div class="step-header">
            <span class="step-number">1</span>
            <h3>기본 정보</h3>
          </div>
          <div class="form-group">
            <label>게시판 이름 <span class="required">*</span></label>
            <input v-model="formData.name" type="text">
          </div>

          <div class="form-group">
            <label>게시판 목록 URL <span class="required">*</span></label>
            <input v-model="formData.url" type="text" placeholder="예: https://example.com/board/list">
            <small class="input-hint">💡 게시판 목록 페이지 URL을 입력하세요</small>
          </div>

          <div class="form-group">
            <label>샘플 게시글 URL <span class="required">*</span></label>
            <input 
              v-model="formData.sampleUrls" 
              type="text"
              placeholder="예: https://example.com/board/view/123"
            >
            <small class="input-hint">💡 본문 셀렉터 추천을 위해 실제 게시글 상세 페이지 URL이 필요합니다</small>
          </div>
        </div>

        <!-- Step 2: 통합 분석 -->
        <div class="step-section">
          <div class="step-header">
            <span class="step-number">2</span>
            <h3>사이트 분석</h3>
          </div>
          
          <button 
            class="btn-analyze" 
            @click="startAnalysis" 
            :disabled="!formData.sampleUrls || isAnalyzing"
          >
            <span v-if="!isAnalyzing">🔍 본문 셀렉터 분석 시작</span>
            <span v-else class="analyzing">
              <span class="spinner"></span>
              {{ analyzingStatus }}
            </span>
          </button>
          <small v-if="!formData.sampleUrls" class="input-hint" style="display: block; margin-top: 8px; color: var(--danger);">
            ⚠️ 샘플 게시글 URL을 입력해야 분석할 수 있습니다
          </small>

          <!-- 분석 진행 상태 -->
          <div v-if="isAnalyzing" class="analysis-progress">
            <div class="progress-item" :class="{ active: analysisStep === 'selector' }">
              <span class="progress-icon">{{ analysisStep === 'selector' ? '⏳' : '✓' }}</span>
              <span>본문 셀렉터 감지 중...</span>
            </div>
          </div>

          <!-- 셀렉터 결과 -->
          <div v-if="analysisResult?.selectors?.content" class="result-section">
            <div class="result-card">
              <div class="result-header">
                <h4>본문 셀렉터</h4>
              </div>
              <div class="result-content">
                <!-- 추천 셀렉터 (참고용) -->
                <div class="form-group">
                  <label>추천 셀렉터 <span class="hint">(참고용)</span></label>
                  <div class="recommended-selectors">
                    <div 
                      v-for="candidate in analysisResult.selectors.content.candidates" 
                      :key="candidate.selector"
                      class="recommended-item-wrapper"
                    >
                      <div class="recommended-item">
                        <code class="selector-code">{{ candidate.selector }}</code>
                        <div class="recommended-actions">
                          <button 
                            class="btn-preview" 
                            @click="togglePreview(candidate.selector)"
                            :title="expandedPreviews[candidate.selector] ? '미리보기 접기' : '미리보기 보기'"
                          >
                            {{ expandedPreviews[candidate.selector] ? '접기' : '미리보기' }}
                          </button>
                          <button 
                            class="btn-copy" 
                            @click="copyToClipboard(candidate.selector)"
                            title="클립보드에 복사"
                          >
                            복사
                          </button>
                        </div>
                      </div>
                      <!-- 미리보기 아코디언 -->
                      <div 
                        v-if="expandedPreviews[candidate.selector]" 
                        class="preview-content"
                      >
                        <div class="preview-header">
                          <span class="preview-label">추출된 텍스트 ({{ candidate.textLength }}자)</span>
                        </div>
                        <div class="preview-text">
                          {{ candidate.extractedText || '텍스트를 추출할 수 없습니다.' }}
                        </div>
                      </div>
                    </div>
                  </div>
                </div>

                <!-- 사용자 직접 입력 필드 -->
                <div class="form-group">
                  <label>본문 셀렉터 <span class="required">*</span></label>
                  <div class="selector-input-group">
                    <input 
                      v-model="manualContentSelector" 
                      type="text" 
                      placeholder="F12로 확인한 본문 셀렉터를 입력하세요 (예: div.content > p)"
                      class="selector-input"
                      @keyup.enter="previewManualSelector"
                    />
                    <button 
                      class="btn-preview-manual"
                      @click="previewManualSelector"
                      :disabled="!manualContentSelector.trim() || !formData.sampleUrls || isPreviewingManual"
                      title="미리보기"
                    >
                      <span v-if="!isPreviewingManual">미리보기</span>
                      <span v-else class="spinner-small"></span>
                    </button>
                  </div>
                  <small class="input-hint">💡 F12 개발자 도구로 본문 영역의 CSS 셀렉터를 확인하세요</small>
                  
                  <!-- 수동 입력 셀렉터 미리보기 -->
                  <div 
                    v-if="manualPreviewResult && expandedPreviews['manual']" 
                    class="preview-content"
                  >
                    <div class="preview-header">
                      <span class="preview-label">추출된 텍스트 ({{ manualPreviewResult.textLength }}자)</span>
                    </div>
                    <div class="preview-text">
                      {{ manualPreviewResult.extractedText || '텍스트를 추출할 수 없습니다.' }}
                    </div>
                  </div>
                  <div v-if="manualPreviewError" class="error-message-small">
                    ⚠️ {{ manualPreviewError }}
                  </div>
                </div>

                <!-- 첨부파일 셀렉터 입력 필드 -->
                <div class="form-group">
                  <label>첨부파일 셀렉터 <span class="optional">(선택)</span></label>
                  <input 
                    v-model="manualAttachmentSelector" 
                    type="text" 
                    placeholder="첨부파일이 없는 경우 비워두세요 (예: a.download-link)"
                    class="selector-input"
                  />
                  <small class="input-hint">💡 첨부파일이 없는 게시판인 경우 비워두세요</small>
                </div>
              </div>
            </div>
          </div>

          <!-- 에러 메시지 -->
          <div v-if="analysisError" class="error-message">
            <span class="error-icon">⚠️</span>
            <span>{{ analysisError }}</span>
            <button class="btn-retry" @click="startAnalysis">재시도</button>
          </div>
        </div>

        <!-- Step 3: 검증 (선택) -->
        <div v-if="manualContentSelector.trim() !== ''" class="step-section">
          <div class="step-header">
            <span class="step-number">3</span>
            <h3>검증 <span class="optional">(선택)</span></h3>
          </div>
          
          <div class="form-group">
            <label>추가 URL로 테스트</label>
            <div class="validation-input-group">
              <input 
                v-model="validationUrl" 
                type="text" 
                placeholder="https://example.com/post/2"
                @keyup.enter="validateSelector"
              >
              <button 
                class="btn-validate" 
                @click="validateSelector"
                :disabled="!validationUrl || isValidating"
              >
                {{ isValidating ? '검증 중...' : '검증' }}
              </button>
            </div>
          </div>

          <!-- 검증 결과 목록 -->
          <div v-if="validationResults.length > 0" class="validation-results">
            <h4>검증 결과</h4>
            <div 
              v-for="(result, index) in validationResults" 
              :key="index"
              class="validation-result-item"
              :class="{ success: result.success, error: !result.success }"
            >
              <span class="result-icon">{{ result.success ? '✓' : '✗' }}</span>
              <div class="result-details">
                <div class="result-url">{{ result.url }}</div>
                <div v-if="result.success" class="result-text">
                  추출된 텍스트 길이: {{ result.textLength }}자
                  <div class="preview-snippet">{{ result.extractedText?.substring(0, 100) }}...</div>
                </div>
                <div v-else class="result-error">{{ result.error }}</div>
              </div>
            </div>
          </div>
        </div>
      </div>

      <div class="modal-footer">
        <button class="btn-cancel" @click="$emit('close')">취소</button>
        <button 
          class="btn-primary" 
          @click="submitForm" 
          :disabled="!isFormComplete"
        >
          게시판 추가
        </button>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, computed } from 'vue';
import type { AnalyzeSiteResponse, ValidationResult, SelectorCandidate } from '@/types/crawling.types';
import { analyzeContent, testSelector } from '@/services/common/crawling.service';

interface ServiceFormData {
  name: string;
  url: string;
  contentSelector: string;
  attachmentSelector?: string;
  useSelenium: boolean;
}

defineProps<{
  domainId: number | string;
  domainBaseUrl: string;
}>();

const emit = defineEmits<{
  close: [];
  create: [service: ServiceFormData];
}>();

const formData = ref({
  name: '',
  url: '',
  sampleUrls: '', // 쉼표로 구분된 여러 URL
});

// 분석 관련 상태
const isAnalyzing = ref(false);
const analysisStep = ref<'selector' | null>(null);
const analyzingStatus = ref('');
const analysisResult = ref<AnalyzeSiteResponse | null>(null);
const analysisError = ref<string | null>(null);

// 셀렉터 관련 상태
const manualContentSelector = ref('');
const manualAttachmentSelector = ref('');

// 검증 관련 상태
const validationUrl = ref('');
const isValidating = ref(false);
const validationResults = ref<ValidationResult[]>([]);

// 미리보기 관련 상태
const expandedPreviews = ref<Record<string, boolean>>({});
const isPreviewingManual = ref(false);
const manualPreviewResult = ref<{ extractedText: string; textLength: number } | null>(null);
const manualPreviewError = ref<string | null>(null);

// 폼 완성 여부
const isFormComplete = computed(() => {
  return formData.value.name && 
         formData.value.url && 
         manualContentSelector.value.trim() !== '';
});

// 통합 분석 시작
const startAnalysis = async () => {
  // 샘플 게시글 URL이 필수
  if (!formData.value.sampleUrls) {
    alert('본문 셀렉터 분석을 위해 샘플 게시글 URL을 입력해주세요.');
    return;
  }

  isAnalyzing.value = true;
  analysisError.value = null;
  analysisResult.value = null;
  analysisStep.value = 'selector';
  analyzingStatus.value = '본문 셀렉터 감지 중...';

  try {
    // 샘플 URL 파싱 (쉼표로 구분된 여러 URL 지원)
    const sampleUrls: string[] = formData.value.sampleUrls
      .split(',')
      .map((url: string) => url.trim())
      .filter(Boolean);

    if (sampleUrls.length === 0) {
      throw new Error('유효한 게시글 URL을 입력해주세요.');
    }

    // 첫 번째 게시글 URL로 분석 (본문 셀렉터 추천용)
    const firstUrl = sampleUrls[0];
    analyzingStatus.value = `게시글 분석 중: ${firstUrl}`;
    analysisResult.value = await analyzeContent({ url: firstUrl });

  } catch (error) {
    analysisError.value = error instanceof Error ? error.message : '분석 중 오류가 발생했습니다.';
    console.error('Analysis error:', error);
  } finally {
    isAnalyzing.value = false;
    analysisStep.value = null;
    analyzingStatus.value = '';
  }
};

// 클립보드에 복사
const copyToClipboard = async (text: string) => {
  try {
    await navigator.clipboard.writeText(text);
    console.log('복사됨:', text);
  } catch (err) {
    console.error('복사 실패:', err);
  }
};

// 미리보기 토글
const togglePreview = (selector: string) => {
  expandedPreviews.value[selector] = !expandedPreviews.value[selector];
};

// 수동 입력 셀렉터 미리보기
const previewManualSelector = async () => {
  if (!manualContentSelector.value.trim() || !formData.value.sampleUrls) {
    return;
  }

  isPreviewingManual.value = true;
  manualPreviewError.value = null;
  manualPreviewResult.value = null;

  try {
    // 샘플 URL 파싱 (첫 번째 URL 사용)
    const sampleUrls: string[] = formData.value.sampleUrls
      .split(',')
      .map((url: string) => url.trim())
      .filter(Boolean);

    if (sampleUrls.length === 0) {
      throw new Error('샘플 게시글 URL을 입력해주세요.');
    }

    const firstUrl = sampleUrls[0];
    const result = await testSelector({
      url: firstUrl,
      selector: manualContentSelector.value.trim(),
    });

    if (result.success) {
      manualPreviewResult.value = {
        extractedText: result.extractedText || '',
        textLength: result.textLength || 0,
      };
      // 미리보기 자동으로 펼치기
      expandedPreviews.value['manual'] = true;
    } else {
      manualPreviewError.value = result.error || '텍스트를 추출할 수 없습니다.';
    }
  } catch (error) {
    manualPreviewError.value = error instanceof Error ? error.message : '미리보기 중 오류가 발생했습니다.';
    console.error('미리보기 에러:', error);
  } finally {
    isPreviewingManual.value = false;
  }
};

// 셀렉터 검증
const validateSelector = async () => {
  if (!validationUrl.value || !manualContentSelector.value) {
    return;
  }

  isValidating.value = true;

  try {
    // 실제 API 호출로 셀렉터 검증
    const analysisResult = await analyzeContent({ url: validationUrl.value });
    
    if (analysisResult.status === 'success' && analysisResult.selectors?.content) {
      const selector = manualContentSelector.value;
      const candidates = analysisResult.selectors.content.candidates || [];
      // Array.find() 대신 for 루프 사용 (ES5 호환)
      let matched: SelectorCandidate | undefined;
      for (let i = 0; i < candidates.length; i++) {
        if (candidates[i].selector === selector) {
          matched = candidates[i];
          break;
        }
      }
      
      const result: ValidationResult = {
        url: validationUrl.value,
        success: !!matched,
        extractedText: matched?.extractedText || '셀렉터와 일치하는 요소를 찾을 수 없습니다.',
        textLength: matched?.textLength || 0,
        error: matched ? undefined : '셀렉터로 요소를 찾을 수 없습니다.',
      };

      validationResults.value.push(result);
    } else {
      validationResults.value.push({
        url: validationUrl.value,
        success: false,
        error: 'URL 분석에 실패했습니다.',
      });
    }
    
    validationUrl.value = ''; // 입력 필드 초기화
  } catch (error) {
    validationResults.value.push({
      url: validationUrl.value,
      success: false,
      error: error instanceof Error ? error.message : '검증 중 오류가 발생했습니다.',
    });
  } finally {
    isValidating.value = false;
  }
};

// 폼 제출
const submitForm = () => {
  if (!formData.value.name || !formData.value.url) {
    alert('모든 필수 필드를 채워주세요');
    return;
  }

  if (!manualContentSelector.value.trim()) {
    alert('본문 셀렉터를 입력해주세요');
    return;
  }

  emit('create', {
    name: formData.value.name,
    url: formData.value.url,
    contentSelector: manualContentSelector.value.trim(),
    attachmentSelector: manualAttachmentSelector.value.trim() || undefined,
    useSelenium: false, // 기본값: HTTP 사용
  });
};
</script>

<style scoped>
.modal-content {
  display: flex;
  flex-direction: column;
  max-height: 90vh;
  width: 100%;
  max-width: 600px;
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

.step-section {
  margin-bottom: 32px;
  padding-bottom: 24px;
  border-bottom: 2px solid var(--border);
}

.step-section:last-child {
  border-bottom: none;
}

.step-header {
  display: flex;
  align-items: center;
  gap: 12px;
  margin-bottom: 20px;
}

.step-number {
  display: flex;
  align-items: center;
  justify-content: center;
  width: 28px;
  height: 28px;
  background: var(--primary);
  color: white;
  border-radius: 50%;
  font-weight: 600;
  font-size: 14px;
}

.step-header h3 {
  font-size: 16px;
  font-weight: 600;
  margin: 0;
}

.optional {
  font-size: 13px;
  font-weight: normal;
  color: var(--text-secondary);
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

.hint {
  font-size: 12px;
  font-weight: normal;
  color: var(--text-secondary);
}

.form-group input,
.form-group select {
  width: 100%;
  padding: 10px;
  border: 1px solid var(--border);
  border-radius: 6px;
  font-size: 14px;
}

.btn-analyze {
  width: 100%;
  padding: 12px;
  background: var(--primary);
  color: white;
  border: none;
  border-radius: 6px;
  font-size: 15px;
  font-weight: 500;
  cursor: pointer;
  transition: background 0.2s;
}

.btn-analyze:hover:not(:disabled) {
  background: var(--primary-dark);
}

.btn-analyze:disabled {
  opacity: 0.6;
  cursor: not-allowed;
}

.analyzing {
  display: flex;
  align-items: center;
  gap: 8px;
}

.spinner {
  width: 16px;
  height: 16px;
  border: 2px solid rgba(255, 255, 255, 0.3);
  border-top-color: white;
  border-radius: 50%;
  animation: spin 0.8s linear infinite;
}

@keyframes spin {
  to { transform: rotate(360deg); }
}

.analysis-progress {
  margin-top: 16px;
  padding: 16px;
  background: var(--bg-light);
  border-radius: 6px;
}

.progress-item {
  display: flex;
  align-items: center;
  gap: 12px;
  padding: 8px 0;
  color: var(--text-secondary);
  font-size: 14px;
}

.progress-item.active {
  color: var(--text-primary);
  font-weight: 500;
}

.progress-icon {
  font-size: 16px;
}

.result-section {
  margin-top: 20px;
}

.result-card {
  background: var(--bg-light);
  border-radius: 8px;
  padding: 16px;
  border: 1px solid var(--border);
}

.result-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 16px;
}

.result-header h4 {
  font-size: 15px;
  font-weight: 600;
  margin: 0;
}

.btn-reanalyze {
  padding: 6px 12px;
  background: white;
  border: 1px solid var(--border);
  border-radius: 4px;
  font-size: 12px;
  cursor: pointer;
}

.btn-reanalyze:hover:not(:disabled) {
  background: var(--bg-light);
}

.btn-reanalyze:disabled {
  opacity: 0.5;
  cursor: not-allowed;
}

.result-content {
  display: flex;
  flex-direction: column;
  gap: 16px;
}

.result-item {
  display: flex;
  gap: 8px;
  font-size: 14px;
}

.result-item .label {
  font-weight: 500;
  color: var(--text-secondary);
}

.result-item .value {
  font-weight: 600;
}

.result-item .value.static {
  color: var(--success);
}

.result-item .value.dynamic {
  color: var(--warning);
}

.selector-input {
  width: 100%;
}

.recommended-selectors {
  display: flex;
  flex-direction: column;
  gap: 8px;
  margin-top: 8px;
}

.recommended-item-wrapper {
  display: flex;
  flex-direction: column;
  gap: 0;
}

.recommended-item {
  display: flex;
  align-items: center;
  gap: 8px;
  padding: 8px 12px;
  background: var(--bg-light);
  border: 1px solid var(--border);
  border-radius: 6px;
}

@media (max-width: 768px) {
  .recommended-item {
    flex-direction: column;
    align-items: stretch;
  }

  .recommended-actions {
    width: 100%;
    display: flex;
    gap: 8px;
  }

  .btn-preview,
  .btn-copy {
    flex: 1;
  }
}

.recommended-actions {
  display: flex;
  gap: 6px;
}

.selector-code {
  flex: 1;
  font-family: 'Monaco', 'Courier New', monospace;
  font-size: 13px;
  color: var(--text-primary);
  background: white;
  padding: 4px 8px;
  border-radius: 4px;
}

.btn-preview {
  padding: 4px 12px;
  background: var(--bg-light);
  color: var(--text-primary);
  border: 1px solid var(--border);
  border-radius: 4px;
  font-size: 12px;
  cursor: pointer;
  transition: all 0.2s;
  white-space: nowrap;
}

.btn-preview:hover {
  background: var(--border);
}

.btn-copy {
  padding: 4px 12px;
  background: var(--primary);
  color: white;
  border: none;
  border-radius: 4px;
  font-size: 12px;
  cursor: pointer;
  transition: background 0.2s;
  white-space: nowrap;
}

.btn-copy:hover {
  background: var(--primary-dark);
}

.preview-content {
  margin-top: 8px;
  padding: 12px;
  background: white;
  border: 1px solid var(--border);
  border-radius: 6px;
  border-top-left-radius: 0;
  border-top-right-radius: 0;
  border-top: none;
}

.preview-header {
  margin-bottom: 8px;
  padding-bottom: 8px;
  border-bottom: 1px solid var(--border);
}

.preview-label {
  font-size: 12px;
  font-weight: 500;
  color: var(--text-secondary);
}

.preview-text {
  font-size: 13px;
  line-height: 1.6;
  color: var(--text-primary);
  max-height: 300px;
  overflow-y: auto;
  white-space: pre-wrap;
  word-break: break-word;
}

.input-hint {
  display: block;
  font-size: 12px;
  color: var(--text-secondary);
  margin-top: 6px;
}

.selector-input-group {
  display: flex;
  gap: 8px;
  align-items: stretch;
}

@media (max-width: 768px) {
  .selector-input-group {
    flex-direction: column;
  }

  .btn-preview-manual {
    width: 100%;
  }
}

.selector-input-group .selector-input {
  flex: 1;
}

.btn-preview-manual {
  padding: 10px 16px;
  background: var(--primary);
  color: white;
  border: none;
  border-radius: 6px;
  font-size: 13px;
  font-weight: 500;
  cursor: pointer;
  white-space: nowrap;
  transition: background 0.2s;
}

.btn-preview-manual:hover:not(:disabled) {
  background: var(--primary-dark);
}

.btn-preview-manual:disabled {
  opacity: 0.5;
  cursor: not-allowed;
}

.spinner-small {
  display: inline-block;
  width: 12px;
  height: 12px;
  border: 2px solid rgba(255, 255, 255, 0.3);
  border-top-color: white;
  border-radius: 50%;
  animation: spin 0.6s linear infinite;
}

.error-message {
  display: flex;
  align-items: center;
  gap: 12px;
  padding: 12px;
  background: #fee2e2;
  border: 1px solid #fecaca;
  border-radius: 6px;
  color: #991b1b;
  font-size: 14px;
  margin-top: 16px;
}

.error-message-small {
  margin-top: 8px;
  padding: 8px 12px;
  background: #fee2e2;
  border: 1px solid #fecaca;
  border-radius: 4px;
  color: #991b1b;
  font-size: 12px;
}

.error-icon {
  font-size: 18px;
}

.btn-retry {
  margin-left: auto;
  padding: 6px 12px;
  background: white;
  border: 1px solid #fecaca;
  border-radius: 4px;
  font-size: 12px;
  color: #991b1b;
  cursor: pointer;
}

.btn-retry:hover {
  background: #fecaca;
}

.validation-input-group {
  display: flex;
  gap: 8px;
}

@media (max-width: 768px) {
  .validation-input-group {
    flex-direction: column;
  }

  .btn-validate {
    width: 100%;
  }
}

.validation-input-group input {
  flex: 1;
}

.btn-validate {
  padding: 10px 20px;
  background: var(--bg-light);
  border: 1px solid var(--border);
  border-radius: 6px;
  font-size: 14px;
  cursor: pointer;
  white-space: nowrap;
}

.btn-validate:hover:not(:disabled) {
  background: var(--border);
}

.btn-validate:disabled {
  opacity: 0.5;
  cursor: not-allowed;
}

.validation-results {
  margin-top: 16px;
}

.validation-results h4 {
  font-size: 14px;
  font-weight: 600;
  margin-bottom: 12px;
}

.validation-result-item {
  display: flex;
  gap: 12px;
  padding: 12px;
  border-radius: 6px;
  margin-bottom: 8px;
  border: 1px solid var(--border);
}

.validation-result-item.success {
  background: #f0fdf4;
  border-color: #bbf7d0;
}

.validation-result-item.error {
  background: #fee2e2;
  border-color: #fecaca;
}

.result-icon {
  font-size: 18px;
  flex-shrink: 0;
}

.result-details {
  flex: 1;
  font-size: 13px;
}

.result-url {
  font-weight: 500;
  margin-bottom: 4px;
  word-break: break-all;
}

.result-text {
  color: var(--text-secondary);
  font-size: 12px;
}

.preview-snippet {
  margin-top: 4px;
  padding: 8px;
  background: white;
  border-radius: 4px;
  font-size: 11px;
  color: var(--text-secondary);
  max-height: 60px;
  overflow-y: auto;
}

.result-error {
  color: #991b1b;
  font-size: 12px;
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

