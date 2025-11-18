<template>
  <div class="modal-overlay" @click.self="$emit('close')">
    <div class="modal-content large">
      <div class="modal-header">
        <h2>게시물 상세 내용</h2>
        <button class="btn-close" @click="$emit('close')">×</button>
      </div>

      <div class="modal-body">
        <div class="content-section">
          <h3 class="content-title">본문 내용</h3>
          <div class="post-content-box">
            <div class="post-content">
              {{ post.content }}
            </div>
          </div>
        </div>

        <div class="attachments-section">
          <h3 class="attachments-title">첨부파일</h3>
          <div class="attachments-box">
            <div class="attachments-content">
              <div v-if="post.attachments && post.attachments.length > 0">
                <div v-for="(file, idx) in post.attachments" :key="idx" class="attachment-item">
                  <span class="file-icon">📄</span>
                  <span>{{ file.name }}</span>
                  <span class="file-size">{{ file.size }}</span>
                </div>
              </div>
              <div v-else class="empty-attachments">
                첨부파일이 없습니다.
              </div>
            </div>
          </div>
        </div>
      </div>

      <div class="modal-footer">
        <button class="btn-cancel" @click="$emit('close')">닫기</button>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import type { Post } from '@/types/crawling.types';

defineProps<{
  post: Post;
}>();

defineEmits<{
  close: [];
}>();
</script>

<style scoped>
.modal-content.large {
  max-width: 700px;
  display: flex;
  flex-direction: column;
  max-height: 90vh;
  width: 100%;
  margin: 0 auto;
}

/* 모바일 반응형 */
@media (max-width: 768px) {
  .modal-content.large {
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

  .modal-header h2 {
    font-size: 16px;
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

.post-meta {
  margin-bottom: 20px;
  padding: 12px;
  background: var(--bg-light);
  border-radius: 6px;
  font-size: 13px;
  line-height: 1.8;
}

.post-meta a {
  display: block;
}

.content-section {
  margin-bottom: 20px;
}

.content-title {
  font-size: 14px;
  font-weight: 600;
  margin-bottom: 8px;
  color: var(--text-primary);
}

.post-content-box {
  padding: 16px;
  background: var(--bg-light);
  border: 1px solid var(--border);
  border-radius: 6px;
}

.post-content {
  line-height: 1.8;
  white-space: pre-wrap;
  word-wrap: break-word;
  color: var(--text-primary);
  min-height: 100px;
}

.attachments-section {
  margin-top: 20px;
}

.attachments-title {
  font-size: 14px;
  font-weight: 600;
  margin-bottom: 8px;
  color: var(--text-primary);
}

.attachments-box {
  padding: 16px;
  background: var(--bg-light);
  border: 1px solid var(--border);
  border-radius: 6px;
}

.attachments-content {
  min-height: 60px;
}

.empty-attachments {
  color: var(--text-secondary);
  font-size: 13px;
  text-align: center;
  padding: 20px;
  font-style: italic;
}

.attachment-item {
  display: flex;
  align-items: center;
  gap: 12px;
  padding: 8px 12px;
  background: var(--bg-light);
  border-radius: 6px;
  margin-bottom: 8px;
  font-size: 13px;
}

.file-icon {
  font-size: 16px;
}

.file-size {
  margin-left: auto;
  color: var(--text-secondary);
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
  .post-content-box,
  .attachments-box {
    padding: 12px;
  }

  .post-content {
    font-size: 14px;
  }
}
</style>

