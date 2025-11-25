<template>
  <div class="post-list-container">
    <!-- 데스크톱 테이블 뷰 -->
    <div class="table-wrapper">
      <table class="desktop-table">
      <thead>
        <tr>
          <th style="width: 60px;">번호</th>
          <th>제목</th>
          <th>URL</th>
          <th>작성일</th>
        </tr>
      </thead>
      <tbody>
        <tr
          v-for="(post, index) in paginatedPosts"
          :key="post.id"
          @click="$emit('view-post', post)"
          style="cursor: pointer;"
        >
          <td class="number-cell">{{ getPostNumber(index) }}</td>
          <td class="title-cell">{{ truncateText(post.title, 50) }}</td>
          <td class="url-cell">
            <a :href="post.url" target="_blank" @click.stop :title="post.url">
              {{ truncateText(post.url, 60) }}
            </a>
          </td>
          <td class="date-cell">{{ formatDate(post.postAt) }}</td>
        </tr>
      </tbody>
      </table>
    </div>

    <!-- 모바일 카드 뷰 -->
    <div class="mobile-cards">
      <div
        v-for="(post, index) in paginatedPosts"
        :key="post.id"
        class="post-card"
        @click="$emit('view-post', post)"
      >
        <div class="card-header">
          <div class="card-title-wrapper">
            <span class="card-number">{{ getPostNumber(index) }}</span>
            <h3 class="card-title">{{ post.title }}</h3>
          </div>
        </div>
        <div class="card-url">
          <a :href="post.url" target="_blank" @click.stop :title="post.url">
            {{ truncateText(post.url, 50) }}
          </a>
        </div>
        <div class="card-date">{{ formatDate(post.postAt) }}</div>
      </div>
    </div>

    <!-- 페이지네이션 -->
    <div class="pagination">
      <button
        class="pagination-btn"
        :disabled="currentPage === 1"
        @click="goToPage(currentPage - 1)"
      >
        이전
      </button>
      <div class="pagination-pages">
        <button
          v-for="page in visiblePages"
          :key="page"
          class="pagination-page"
          :class="{ active: page === currentPage }"
          @click="goToPage(page)"
        >
          {{ page }}
        </button>
      </div>
      <button
        class="pagination-btn"
        :disabled="currentPage === totalPages"
        @click="goToPage(currentPage + 1)"
      >
        다음
      </button>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, watch } from 'vue';
import type { Post } from '@/types/crawling.types';

const props = defineProps<{
  posts: Post[];
}>();

defineEmits<{
  'view-post': [post: Post];
}>();

// 페이지네이션 설정
const itemsPerPage = 15;
const currentPage = ref(1);

// posts가 변경되면 첫 페이지로 리셋
watch(() => props.posts, () => {
  currentPage.value = 1;
});

// 총 페이지 수
const totalPages = computed(() => {
  return Math.ceil(props.posts.length / itemsPerPage);
});

// 게시글은 최신순으로 유지 (정렬하지 않음)
// 현재 페이지의 게시글 (최신순)
const paginatedPosts = computed(() => {
  const start = (currentPage.value - 1) * itemsPerPage;
  const end = start + itemsPerPage;
  return props.posts.slice(start, end);
});

// 게시글 번호 계산 (가장 오래된 것이 1번)
// 전체 게시글 중 가장 오래된 것이 1번이 되도록 역순으로 계산
const getPostNumber = (index: number): number => {
  const totalPosts = props.posts.length;
  const start = (currentPage.value - 1) * itemsPerPage;
  const currentIndex = start + index;
  // 전체 개수에서 역순으로 계산 (마지막 게시글이 1번)
  return totalPosts - currentIndex;
};

// 표시할 페이지 번호들 (최대 5개)
const visiblePages = computed(() => {
  const pages: number[] = [];
  const maxVisible = 5;
  let start = Math.max(1, currentPage.value - Math.floor(maxVisible / 2));
  let end = Math.min(totalPages.value, start + maxVisible - 1);
  
  // 끝에서 시작점 조정
  if (end - start < maxVisible - 1) {
    start = Math.max(1, end - maxVisible + 1);
  }
  
  for (let i = start; i <= end; i++) {
    pages.push(i);
  }
  
  return pages;
});

// 페이지 이동
const goToPage = (page: number) => {
  if (page >= 1 && page <= totalPages.value) {
    currentPage.value = page;
    // 페이지 상단으로 스크롤
    window.scrollTo({ top: 0, behavior: 'smooth' });
  }
};

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
  display: flex;
  flex-direction: column;
  overflow: hidden;
  padding: 0;
}

/* 테이블 래퍼 */
.table-wrapper {
  flex: 1;
  overflow-y: auto;
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

.number-cell {
  text-align: center;
  color: var(--text-secondary);
  font-weight: 500;
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

.card-title-wrapper {
  display: flex;
  align-items: flex-start;
  gap: 8px;
  flex: 1;
}

.card-number {
  color: var(--text-secondary);
  font-weight: 500;
  font-size: 14px;
  flex-shrink: 0;
  margin-top: 2px;
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

/* 페이지네이션 */
.pagination {
  display: flex;
  justify-content: center;
  align-items: center;
  gap: 8px;
  padding: 20px;
  border-top: 1px solid var(--border);
  background: white;
  flex-shrink: 0;
}

.pagination-btn {
  padding: 8px 16px;
  background: white;
  border: 1px solid var(--border);
  border-radius: 6px;
  font-size: 14px;
  cursor: pointer;
  transition: all 0.2s;
  color: var(--text-primary);
}

.pagination-btn:hover:not(:disabled) {
  background: var(--bg-light);
  border-color: var(--primary);
}

.pagination-btn:disabled {
  opacity: 0.5;
  cursor: not-allowed;
}

.pagination-pages {
  display: flex;
  gap: 4px;
}

.pagination-page {
  min-width: 36px;
  height: 36px;
  padding: 0 8px;
  background: white;
  border: 1px solid var(--border);
  border-radius: 6px;
  font-size: 14px;
  cursor: pointer;
  transition: all 0.2s;
  color: var(--text-primary);
  display: flex;
  align-items: center;
  justify-content: center;
}

.pagination-page:hover {
  background: var(--bg-light);
  border-color: var(--primary);
}

.pagination-page.active {
  background: var(--primary);
  color: white;
  border-color: var(--primary);
}

.pagination-page.active:hover {
  background: var(--primary-dark);
}

/* 모바일 반응형 */
@media (max-width: 768px) {
  .table-wrapper {
    display: none;
  }

  .mobile-cards {
    display: flex;
    flex-direction: column;
    flex: 1;
    overflow-y: auto;
  }

  .post-list-container {
    padding: 0;
  }
}
</style>

