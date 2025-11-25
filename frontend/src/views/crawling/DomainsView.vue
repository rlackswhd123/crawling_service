<template>
  <div class="domains-container crawling-container">
    <!-- Mobile Overlay -->
    <div v-if="showSidebar" class="sidebar-overlay" @click="showSidebar = false"></div>
    
    <!-- Left Sidebar -->
    <DomainSidebar
      :domains="domains"
      :selected-domain-id="selectedDomainId"
      :selected-service-id="selectedServiceId"
      :class="{ 'sidebar-open': showSidebar }"
      @select-service="handleSelectService"
      @open-create-modal="showDomainCreateModal = true"
      @open-create-service-modal="openServiceCreateModal"
      @edit-domain="editDomain"
      @edit-service="editService"
      @delete-domain="deleteDomain"
      @delete-service="deleteService"
    />

    <!-- Right Main Content -->
    <div class="main-content">
      <div class="header">
        <button class="btn-menu-toggle" @click="showSidebar = !showSidebar" title="메뉴">
          ☰
        </button>
        <div class="header-content">
          <h1>{{ selectedServiceName || selectedDomain?.name || '도메인 선택' }}</h1>
          <div v-if="selectedServiceName" class="service-breadcrumb">
            {{ selectedDomain?.name }} > {{ selectedServiceName }}
          </div>
        </div>
        <button 
          class="btn-primary" 
          @click="showCrawlStartModal = true"
          :disabled="!selectedServiceId"
        >
          ▶ 크롤링 시작
        </button>
      </div>

      <CrawledPostList
        :posts="selectedDomainPosts"
        @view-post="viewPost"
      />
    </div>

    <!-- Modals -->
    <DomainCreateModal
      v-if="showDomainCreateModal"
      @close="showDomainCreateModal = false"
      @create="createDomain"
    />

    <ServiceCreateModal
      v-if="showServiceCreateModal && selectedDomainForService"
      :domain-id="selectedDomainForService.id"
      :domain-base-url="selectedDomainForService.baseUrl"
      @close="showServiceCreateModal = false"
      @create="createService"
    />

    <CrawlStartModal
      v-if="showCrawlStartModal && selectedDomain && selectedService"
      :domain="selectedDomain"
      :service="selectedService"
      @close="showCrawlStartModal = false"
      @start="startCrawl"
    />

    <PostDetailModal
      v-if="selectedPost"
      :post="selectedPost"
      @close="selectedPost = null"
    />
  </div>
</template>

<script setup lang="ts">
import { ref, computed, onMounted } from 'vue';
import type { Domain, Service, Post, CrawlConfig } from '@/types/crawling.types';
import DomainSidebar from '@/components/crawling/DomainSidebar.vue';
import CrawledPostList from '@/components/crawling/CrawledPostList.vue';
import DomainCreateModal from '@/components/crawling/DomainCreateModal.vue';
import ServiceCreateModal from '@/components/crawling/ServiceCreateModal.vue';
import CrawlStartModal from '@/components/crawling/CrawlStartModal.vue';
import PostDetailModal from '@/components/crawling/PostDetailModal.vue';
import { startCrawl as startCrawlAPI, getPosts as getPostsAPI } from '@/services/common/crawling.service';
import { 
  getDomains, 
  createDomain as createDomainAPI, 
  deleteDomain as deleteDomainAPI, 
  getServices, 
  createService as createServiceAPI,
  deleteService as deleteServiceAPI
} from '@/services/common/domain.service';
import type { Service as ServiceType } from '@/services/common/domain.service';

// State
const domains = ref<Domain[]>([]);
const posts = ref<Record<string, Post[]>>({});
const isLoading = ref(false);

const selectedDomainId = ref<number | string | null>(null);
const selectedServiceId = ref<number | string | null>(null);
const showDomainCreateModal = ref(false);
const showServiceCreateModal = ref(false);
const selectedDomainForService = ref<Domain | null>(null);
const showCrawlStartModal = ref(false);
const selectedPost = ref<Post | null>(null);
const showSidebar = ref(false);

// Computed
const selectedDomain = computed(() => 
  selectedDomainId.value ? domains.value.find((d: Domain) => d.id === selectedDomainId.value) : null
);

const selectedService = computed(() => {
  if (!selectedDomain.value || !selectedServiceId.value) return null;
  return selectedDomain.value.services?.find((s: Service) => s.id === selectedServiceId.value) || null;
});

const selectedServiceName = computed(() => selectedService.value?.name || null);

const selectedDomainPosts = computed(() => {
  if (!selectedDomainId.value || !selectedServiceId.value) return [];
  const key = `${selectedDomainId.value}-${selectedServiceId.value}`;
  return posts.value[key] || [];
});

// 도메인 목록 로드
const loadDomains = async () => {
  isLoading.value = true;
  try {
    const domainList = await getDomains();
    
    // 각 도메인의 서비스도 함께 로드
    const domainsWithServices = await Promise.all(
      domainList.map(async (domain) => {
        try {
          const services = await getServices(domain.id);
          return {
            ...domain,
            id: domain.id, // UUID는 그대로 사용
            services: services.map((s: ServiceType) => ({
              id: s.id, // UUID는 그대로 사용
              name: s.name,
              url: s.url,
              contentSelector: s.contentSelector || '',
              attachmentSelector: s.attachmentSelector,
            }))
          };
        } catch (error) {
          console.error(`서비스 로드 실패 (${domain.id}):`, error);
          return {
            ...domain,
            id: domain.id, // UUID는 그대로 사용
            services: []
          };
        }
      })
    );
    
    domains.value = domainsWithServices as Domain[];
  } catch (error: any) {
    console.error('도메인 목록 로드 실패:', error);
    const errorMessage = error?.message || error?.detail || '도메인 목록을 불러오는데 실패했습니다.';
    alert(`도메인 목록을 불러오는데 실패했습니다.\n${errorMessage}\n\nAPI 서버가 실행 중인지 확인해주세요.`);
  } finally {
    isLoading.value = false;
  }
};

// 컴포넌트 마운트 시 도메인 로드
onMounted(() => {
  loadDomains();
});

// Methods
const selectService = async (domainId: number | string, serviceId: number | string) => {
  selectedDomainId.value = domainId;
  selectedServiceId.value = serviceId;
  
  // 서비스 선택 시 게시글 목록 로드
  await loadPosts(domainId, serviceId);
};

const handleSelectService = async (domainId: number | string, serviceId: number | string) => {
  await selectService(domainId, serviceId);
  // 모바일에서 서비스 선택 시 사이드바 닫기
  showSidebar.value = false;
};

// 게시글 목록 로드
const loadPosts = async (domainId: number | string, serviceId: number | string) => {
  if (!domainId || !serviceId) return;
  
  isLoading.value = true;
  try {
    const postsData = await getPostsAPI({
      domainId: String(domainId),
      serviceId: String(serviceId),
      limit: 10000,  // 충분히 큰 값으로 설정하여 모든 데이터 가져오기
      offset: 0
    });
    
    // Post 타입으로 변환
    const key = `${domainId}-${serviceId}`;
    posts.value[key] = postsData.map((p: any) => ({
      id: p.id,
      post_id: p.post_id || p.id,  // post_id 우선, 없으면 id 사용
      title: p.title,
      url: p.url,
      postAt: p.postAt || p.crawledAt,
      content: p.contentText || p.content || '',  // 텍스트 본문 우선, 없으면 HTML
      selector: '',  // 사용하지 않음
      attachments: (p.attachments || []).map((att: any) => ({
        name: att.name || att.url || '첨부파일',
        size: att.size ? `${att.size} bytes` : '',
        url: att.url || null
      }))
    }));
  } catch (error: any) {
    console.error('게시글 목록 로드 실패:', error);
    const key = `${domainId}-${serviceId}`;
    posts.value[key] = [];  // 에러 시 빈 배열
  } finally {
    isLoading.value = false;
  }
};

interface DomainFormData {
  name: string;
}

const isCreatingDomain = ref(false);

const createDomain = async (domain: DomainFormData) => {
  if (isCreatingDomain.value) {
    return; // 이미 생성 중이면 무시
  }
  
  try {
    isCreatingDomain.value = true;
    
    // 도메인 이름만 입력받고, baseUrl은 나중에 서비스 추가 시 설정
    await createDomainAPI({
      name: domain.name,
      baseUrl: '', // 서비스 추가 시 URL 입력
      useSelenium: false
    });
    
    // 도메인 목록 새로고침
    await loadDomains();
    showDomainCreateModal.value = false;
  } catch (error: any) {
    console.error('도메인 생성 실패:', error);
    const errorMessage = error?.message || error?.detail || '도메인 생성에 실패했습니다.';
    alert(`도메인 생성에 실패했습니다.\n${errorMessage}`);
  } finally {
    isCreatingDomain.value = false;
  }
};

interface ServiceFormData {
  name: string;
  url: string;
  contentSelector: string;
  attachmentSelector?: string;
  useSelenium: boolean;
}

const openServiceCreateModal = (domainId: number | string) => {
  const domain = domains.value.find((d: Domain) => d.id === domainId);
  if (domain) {
    selectedDomainForService.value = domain;
    showServiceCreateModal.value = true;
  }
};

const createService = async (service: ServiceFormData) => {
  if (!selectedDomainForService.value) return;
  
  try {
    // domainId는 이미 문자열(UUID)이므로 그대로 사용
    const domainId = typeof selectedDomainForService.value.id === 'string' 
      ? selectedDomainForService.value.id 
      : String(selectedDomainForService.value.id);
    
    await createServiceAPI({
      domainId: domainId,
      name: service.name,
      url: service.url,
      contentSelector: service.contentSelector,
      attachmentSelector: service.attachmentSelector
    });
    
    // 도메인 목록 새로고침
    await loadDomains();
    
    showServiceCreateModal.value = false;
    selectedDomainForService.value = null;
  } catch (error) {
    console.error('서비스 생성 실패:', error);
    alert('서비스 생성에 실패했습니다.');
  }
};

const startCrawl = async (crawlConfig: CrawlConfig) => {
  if (!selectedDomain.value || !selectedService.value) return;
  
  // 본문 셀렉터 확인
  if (!selectedService.value.contentSelector) {
    alert('본문 셀렉터가 설정되지 않았습니다. 게시판 설정에서 본문 셀렉터를 입력해주세요.');
    return;
  }
  
  try {
    console.log('크롤링 시작:', {
      domain: selectedDomain.value,
      service: selectedService.value,
      config: crawlConfig
    });
    
    // 자동 엔드 페이지 탐색 활성화 확인
    if (crawlConfig.autoEndPage) {
      console.log('🔍 자동 엔드 페이지 탐색 활성화됨:', {
        startPage: crawlConfig.startPage,
        endPage: crawlConfig.endPage,
        note: '끝 페이지는 자동으로 감지됩니다 (HTML → Selenium 순서로 시도)'
      });
    }
    
    // 디버깅: 셀렉터 확인
    console.warn('🔍 [크롤링 시작] 셀렉터 확인:', {
      contentSelector: selectedService.value.contentSelector,
      attachmentSelector: selectedService.value.attachmentSelector,
      serviceFull: selectedService.value
    });
    
    // 실제 API 호출
    const result = await startCrawlAPI({
      domain: {
        id: selectedDomain.value.id,
        name: selectedDomain.value.name,
        baseUrl: selectedDomain.value.baseUrl,
        source: selectedDomain.value.source || '',
        useSelenium: selectedDomain.value.useSelenium,
      },
      service: {
        id: selectedService.value.id,
        name: selectedService.value.name,
        url: selectedService.value.url,
        contentSelector: selectedService.value.contentSelector,
        attachmentSelector: selectedService.value.attachmentSelector,
      },
      config: {
        startPage: crawlConfig.startPage,
        endPage: crawlConfig.endPage,
        autoEndPage: crawlConfig.autoEndPage,
        ocrEngine: crawlConfig.ocrEngine,
        pageParam: crawlConfig.pageParam,
      }
    });
    
    if (result.success) {
      alert(`크롤링 성공: ${result.message}`);
      console.log('크롤링 통계:', result.stats);
      
      // 크롤링 완료 후 게시글 목록 새로고침
      if (selectedDomainId.value && selectedServiceId.value) {
        await loadPosts(selectedDomainId.value, selectedServiceId.value);
      }
    } else {
      alert(`크롤링 실패: ${result.error || '알 수 없는 오류'}`);
    }
  } catch (error) {
    console.error('크롤링 중 에러:', error);
    alert(`크롤링 중 에러가 발생했습니다: ${error instanceof Error ? error.message : '알 수 없는 오류'}`);
  } finally {
    showCrawlStartModal.value = false;
  }
};

const viewPost = (post: Post) => {
  selectedPost.value = post;
};

const deleteDomain = async (domainId: number | string) => {
  if (!confirm('정말 이 도메인을 삭제하시겠습니까?')) return;
  
  try {
    const domainIdStr = typeof domainId === 'string' ? domainId : String(domainId);
    await deleteDomainAPI(domainIdStr);
    
    // 선택된 도메인이 삭제되면 선택 해제
    if (selectedDomainId.value === domainId) {
      selectedDomainId.value = null;
      selectedServiceId.value = null;
    }
    
    // 도메인 목록 새로고침
    await loadDomains();
    
    // 해당 도메인의 모든 서비스 게시물도 삭제
    Object.keys(posts.value).forEach((key: string) => {
      const keyStr = String(domainId);
      if (key.indexOf(keyStr) === 0 && key.charAt(keyStr.length) === '-') {
        delete posts.value[key];
      }
    });
  } catch (error) {
    console.error('도메인 삭제 실패:', error);
    alert('도메인 삭제에 실패했습니다.');
  }
};

const deleteService = async (domainId: number | string, serviceId: number | string) => {
  if (!confirm('정말 이 서비스를 삭제하시겠습니까?')) return;
  
  try {
    const serviceIdStr = typeof serviceId === 'string' ? serviceId : String(serviceId);
    await deleteServiceAPI(serviceIdStr);
    
    // 선택된 서비스가 삭제되면 선택 해제
    if (selectedDomainId.value === domainId && selectedServiceId.value === serviceId) {
      selectedServiceId.value = null;
    }
    
    // 도메인 목록 새로고침
    await loadDomains();
    
    // 해당 서비스의 게시물도 삭제
    const key = `${domainId}-${serviceId}`;
    delete posts.value[key];
  } catch (error) {
    console.error('서비스 삭제 실패:', error);
    alert('서비스 삭제에 실패했습니다.');
  }
};


const editDomain = (domainId: number | string) => {
  // TODO: 도메인 편집 모달 구현
  const domain = domains.value.find((d: Domain) => d.id === domainId);
  if (domain) {
    alert(`도메인 편집 기능은 아직 구현되지 않았습니다.\n도메인: ${domain.name}`);
  }
};

const editService = (domainId: number | string, serviceId: number | string) => {
  // TODO: 서비스 편집 모달 구현
  const domain = domains.value.find((d: Domain) => d.id === domainId);
  if (domain) {
    const service = domain.services?.find((s: Service) => s.id === serviceId);
    if (service) {
      alert(`서비스 편집 기능은 아직 구현되지 않았습니다.\n서비스: ${service.name}`);
    }
  }
};
</script>

<style scoped>
.domains-container {
  display: flex;
  height: 100vh;
  background: white;
  position: relative;
}

.main-content {
  flex: 1;
  display: flex;
  flex-direction: column;
  overflow: hidden;
  width: 100%;
}

.sidebar-overlay {
  display: none;
}

.header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 16px 20px;
  border-bottom: 1px solid var(--border);
  background: white;
  gap: 12px;
}

.btn-menu-toggle {
  display: none;
  background: var(--bg-light);
  border: 1px solid var(--border);
  color: var(--text-primary);
  padding: 8px 12px;
  border-radius: 6px;
  font-size: 18px;
  cursor: pointer;
  flex-shrink: 0;
}

.btn-menu-toggle:hover {
  background: var(--border);
}

.header-content {
  flex: 1;
  min-width: 0;
}

.header h1 {
  font-size: 24px;
  font-weight: 600;
  margin: 0;
  word-break: break-word;
}

.service-breadcrumb {
  font-size: 13px;
  color: var(--text-secondary);
  margin-top: 4px;
  word-break: break-word;
}

.btn-primary:disabled {
  opacity: 0.5;
  cursor: not-allowed;
}

.btn-primary {
  background: var(--primary);
  color: white;
  padding: 10px 20px;
  border: none;
  border-radius: 6px;
  font-size: 14px;
  font-weight: 500;
  cursor: pointer;
  white-space: nowrap;
  flex-shrink: 0;
}

.btn-primary:hover {
  background: var(--primary-dark);
}

/* 모바일 반응형 */
@media (max-width: 768px) {
  .btn-menu-toggle {
    display: block;
  }

  .header {
    padding: 12px 16px;
  }

  .header h1 {
    font-size: 18px;
  }

  .btn-primary {
    padding: 8px 12px;
    font-size: 12px;
  }

  .sidebar-overlay {
    display: block;
    position: fixed;
    top: 0;
    left: 0;
    right: 0;
    bottom: 0;
    background: rgba(0, 0, 0, 0.5);
    z-index: 998;
  }
}
</style>

