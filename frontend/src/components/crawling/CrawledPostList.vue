<template>
  <div class="post-list-container">
    <!-- 데스크톱 테이블 뷰 -->
    <table class="desktop-table">
      <thead>
        <tr>
          <th>제목</th>
          <th>URL</th>
          <th>작성일</th>
          <th style="width: 80px;">작업</th>
        </tr>
      </thead>
      <tbody>
        <tr
          v-for="post in posts"
          :key="post.id"
          @click="$emit('view-post', post)"
          style="cursor: pointer;"
        >
          <td class="title-cell">{{ truncateText(post.title, 50) }}</td>
          <td class="url-cell">
            <a :href="post.url" target="_blank" @click.stop :title="post.url">
              {{ truncateText(post.url, 60) }}
            </a>
          </td>
          <td class="date-cell">{{ formatDate(post.postAt) }}</td>
          <td @click.stop>
            <button
              class="btn-delete-post"
              @click.stop="$emit('delete-post', post)"
              title="게시물 삭제"
            >
              삭제
            </button>
          </td>
        </tr>
      </tbody>
    </table>

    <!-- 모바일 카드 뷰 -->
    <div class="mobile-cards">
      <div
        v-for="post in posts"
        :key="post.id"
        class="post-card"
        @click="$emit('view-post', post)"
      >
        <div class="card-header">
          <h3 class="card-title">{{ post.title }}</h3>
          <button
            class="btn-delete-post-mobile"
            @click.stop="$emit('delete-post', post)"
            title="게시물 삭제"
          >
            ×
          </button>
        </div>
        <div class="card-url">
          <a :href="post.url" target="_blank" @click.stop :title="post.url">
            {{ truncateText(post.url, 50) }}
          </a>
        </div>
        <div class="card-date">{{ formatDate(post.postAt) }}</div>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import type { Post } from '@/types/crawling.types';

defineProps<{
  posts: Post[];
}>();

defineEmits<{
  'view-post': [post: Post];
  'delete-post': [post: Post];
}>();

// 텍스트 줄임 함수
const truncateText = (text: string, maxLength: number): string => {
  if (!text) return '';
  if (text.length <= maxLength) return text;
  return text.substring(0, maxLength) + '...';
};

// 날짜 포맷팅 함수 (년월일만)
const formatDate = (dateString: string | undefined): string => {
  if (!dateString) return '-';
  
  try {
    const date = new Date(dateString);
    if (isNaN(date.getTime())) return dateString;
    
    const year = date.getFullYear();
    const month = String(date.getMonth() + 1).padStart(2, '0');
    const day = String(date.getDate()).padStart(2, '0');
    
    return `${year}-${month}-${day}`;
  } catch (e) {
    return dateString;
  }
};
</script>

<style scoped>
.post-list-container {
  flex: 1;
  overflow: auto;
  padding: 0;
}

/* 데스크톱 테이블 */
.desktop-table {
  width: 100%;
  border-collapse: collapse;
  display: table;
}

.mobile-cards {
  display: none;
}

thead th {
  text-align: left;
  padding: 12px;
  background: var(--bg-light);
  border-bottom: 2px solid var(--border);
  font-weight: 600;
  font-size: 13px;
}

tbody td {
  padding: 12px;
  border-bottom: 1px solid var(--border);
  font-size: 13px;
}

tbody tr:hover {
  background: var(--bg-light);
}

.title-cell {
  max-width: 300px;
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
}

.url-cell {
  max-width: 400px;
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
}

.url-cell a {
  color: var(--primary);
  text-decoration: none;
}

.url-cell a:hover {
  text-decoration: underline;
}

.date-cell {
  white-space: nowrap;
  color: var(--text-secondary);
  font-size: 12px;
}

.btn-delete-post {
  background: var(--danger);
  color: white;
  padding: 4px 12px;
  font-size: 12px;
  border-radius: 4px;
  border: none;
  cursor: pointer;
}

.btn-delete-post:hover {
  background: #dc2626;
}

/* 모바일 카드 뷰 */
.mobile-cards {
  display: none;
  padding: 12px;
  gap: 12px;
}

.post-card {
  background: white;
  border: 1px solid var(--border);
  border-radius: 8px;
  padding: 16px;
  margin-bottom: 12px;
  cursor: pointer;
  transition: all 0.2s;
}

.post-card:hover {
  background: var(--bg-light);
  box-shadow: 0 2px 4px rgba(0, 0, 0, 0.1);
}

.card-header {
  display: flex;
  justify-content: space-between;
  align-items: flex-start;
  gap: 12px;
  margin-bottom: 8px;
}

.card-title {
  flex: 1;
  font-size: 15px;
  font-weight: 600;
  margin: 0;
  color: var(--text-primary);
  word-break: break-word;
  line-height: 1.4;
}

.btn-delete-post-mobile {
  background: var(--danger);
  color: white;
  border: none;
  width: 28px;
  height: 28px;
  border-radius: 50%;
  font-size: 18px;
  display: flex;
  align-items: center;
  justify-content: center;
  cursor: pointer;
  flex-shrink: 0;
  padding: 0;
}

.btn-delete-post-mobile:hover {
  background: #dc2626;
}

.card-url {
  margin-bottom: 8px;
}

.card-url a {
  color: var(--primary);
  text-decoration: none;
  font-size: 13px;
  word-break: break-all;
  display: -webkit-box;
  -webkit-line-clamp: 2;
  -webkit-box-orient: vertical;
  overflow: hidden;
}

.card-url a:hover {
  text-decoration: underline;
}

.card-date {
  font-size: 12px;
  color: var(--text-secondary);
}

/* 모바일 반응형 */
@media (max-width: 768px) {
  .desktop-table {
    display: none;
  }

  .mobile-cards {
    display: flex;
    flex-direction: column;
  }

  .post-list-container {
    padding: 0;
  }
}
</style>

