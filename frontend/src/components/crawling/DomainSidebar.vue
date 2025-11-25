<template>
  <div class="sidebar">
    <div class="sidebar-header">
      <h2>웹 도메인 목록</h2>
      <button class="btn-add" @click="$emit('open-create-modal')">+</button>
    </div>
    
    <div class="domain-list">
      <div
        v-for="domain in domains"
        :key="domain.id"
        class="domain-wrapper"
      >
        <div
          class="domain-item"
          :class="{ 
            active: domain.id === selectedDomainId,
            expanded: expandedDomainId === domain.id
          }"
          @click="toggleDomain(domain.id)"
        >
          <div class="domain-content">
            <span class="expand-icon" :class="{ expanded: expandedDomainId === domain.id }">▶</span>
            <span class="domain-name">{{ domain.name }}</span>
          </div>
          <div class="domain-actions" @click.stop>
            <button
              class="btn-more"
              @click.stop="toggleDomainMenu(domain.id)"
              title="더보기"
            >
              ⋯
            </button>
            <div
              v-if="showMenuId === domain.id"
              class="context-menu"
              @click.stop
            >
              <button
                class="menu-item"
                @click.stop="handleAddService(domain.id)"
              >
                추가
              </button>
              <button
                class="menu-item"
                @click.stop="handleEditDomain(domain.id)"
              >
                편집
              </button>
              <button
                class="menu-item menu-item-danger"
                @click.stop="handleDeleteDomain(domain.id)"
              >
                삭제
              </button>
            </div>
          </div>
        </div>
        
        <!-- 서비스 목록 (아코디언) -->
        <div 
          v-if="expandedDomainId === domain.id"
          class="service-list"
          :class="{ 'has-services': domain.services && domain.services.length > 0 }"
        >
          <div
            v-for="service in domain.services"
            :key="service.id"
            class="service-item"
            :class="{ 
              active: domain.id === selectedDomainId && service.id === selectedServiceId 
            }"
            @click.stop="selectService(domain.id, service.id)"
          >
            <span class="service-name">{{ service.name }}</span>
            <div class="service-actions" @click.stop>
              <button
                class="btn-more-service"
                @click.stop="toggleServiceMenu(`${domain.id}-${service.id}`)"
                title="더보기"
              >
                ⋯
              </button>
              <div
                v-if="showMenuKey === `${domain.id}-${service.id}`"
                class="context-menu"
                @click.stop
              >
                <button
                  class="menu-item"
                  @click.stop="handleEditService(domain.id, service.id)"
                >
                  편집
                </button>
                <button
                  class="menu-item menu-item-danger"
                  @click.stop="handleDeleteService(domain.id, service.id)"
                >
                  삭제
                </button>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted, onUnmounted } from 'vue';
import type { Domain } from '@/types/crawling.types';

defineProps<{
  domains: Domain[];
  selectedDomainId: number | string | null;
  selectedServiceId?: number | string | null;
}>();

const emit = defineEmits<{
  'select-service': [domainId: number | string, serviceId: number | string];
  'open-create-modal': [];
  'open-create-service-modal': [domainId: number | string];
  'edit-domain': [domainId: number | string];
  'edit-service': [domainId: number | string, serviceId: number | string];
  'delete-domain': [domainId: number | string];
  'delete-service': [domainId: number | string, serviceId: number | string];
}>();

const expandedDomainId = ref<number | string | null>(null);
const showMenuId = ref<number | string | null>(null);
const showMenuKey = ref<string | null>(null);

const toggleDomain = (domainId: number | string) => {
  if (expandedDomainId.value === domainId) {
    expandedDomainId.value = null;
  } else {
    expandedDomainId.value = domainId;
  }
  // 도메인 토글 시 메뉴 숨기기
  showMenuId.value = null;
  showMenuKey.value = null;
};

const selectService = (domainId: number | string, serviceId: number | string) => {
  emit('select-service', domainId, serviceId);
  // 서비스 선택 시 메뉴 숨기기
  showMenuId.value = null;
  showMenuKey.value = null;
};

const toggleDomainMenu = (domainId: number | string) => {
  if (showMenuId.value === domainId) {
    showMenuId.value = null;
  } else {
    showMenuId.value = domainId;
    showMenuKey.value = null; // 다른 메뉴 닫기
  }
};

const toggleServiceMenu = (key: string) => {
  if (showMenuKey.value === key) {
    showMenuKey.value = null;
  } else {
    showMenuKey.value = key;
    showMenuId.value = null; // 다른 메뉴 닫기
  }
};

const handleAddService = (domainId: number | string) => {
  emit('open-create-service-modal', domainId);
  showMenuId.value = null;
};

const handleEditDomain = (domainId: number | string) => {
  emit('edit-domain', domainId);
  showMenuId.value = null;
};

const handleEditService = (domainId: number | string, serviceId: number | string) => {
  emit('edit-service', domainId, serviceId);
  showMenuKey.value = null;
};

const handleDeleteDomain = (domainId: number | string) => {
  emit('delete-domain', domainId);
  showMenuId.value = null;
};

const handleDeleteService = (domainId: number | string, serviceId: number | string) => {
  emit('delete-service', domainId, serviceId);
  showMenuKey.value = null;
};

// 외부 클릭 시 메뉴 닫기
const handleClickOutside = (event: MouseEvent) => {
  const target = event.target as HTMLElement;
  if (!target.closest('.domain-actions') && !target.closest('.service-actions')) {
    showMenuId.value = null;
    showMenuKey.value = null;
  }
};

onMounted(() => {
  document.addEventListener('click', handleClickOutside);
});

onUnmounted(() => {
  document.removeEventListener('click', handleClickOutside);
});
</script>

<style scoped>
.sidebar {
  width: 280px;
  border-right: 1px solid var(--border);
  display: flex;
  flex-direction: column;
  background: white;
  overflow-y: auto;
  position: relative;
  z-index: 999;
  transition: transform 0.3s ease;
}

/* 모바일 반응형 */
@media (max-width: 768px) {
  .sidebar {
    position: fixed;
    top: 0;
    left: 0;
    bottom: 0;
    width: 280px;
    max-width: 85vw;
    transform: translateX(-100%);
    box-shadow: 2px 0 8px rgba(0, 0, 0, 0.1);
    z-index: 999;
  }

  .sidebar.sidebar-open {
    transform: translateX(0);
  }
}

.sidebar-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 20px;
  border-bottom: 1px solid var(--border);
}

.sidebar-header h2 {
  font-size: 16px;
  font-weight: 600;
}

.btn-add {
  width: 32px;
  height: 32px;
  padding: 0;
  background: var(--success);
  color: white;
  border-radius: 50%;
  font-size: 18px;
  display: flex;
  align-items: center;
  justify-content: center;
}

.domain-list {
  flex: 1;
  overflow-y: auto;
}

.domain-wrapper {
  border-bottom: 1px solid var(--border);
}

.domain-item {
  padding: 12px 20px;
  cursor: pointer;
  transition: all 0.2s;
  border-left: 3px solid transparent;
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 8px;
}

.domain-item:hover {
  background: var(--bg-light);
}

.domain-item.active {
  background: rgba(99, 102, 241, 0.1);
  color: var(--primary);
  border-left-color: var(--primary);
}

.domain-content {
  display: flex;
  align-items: center;
  gap: 8px;
  flex: 1;
}

.expand-icon {
  font-size: 10px;
  transition: transform 0.2s;
  color: var(--text-secondary);
}

.expand-icon.expanded {
  transform: rotate(90deg);
}

.domain-name {
  flex: 1;
}

.service-list {
  background: var(--bg-light);
}

.service-item {
  padding: 10px 20px 10px 48px;
  cursor: pointer;
  transition: all 0.2s;
  border-left: 3px solid transparent;
  font-size: 14px;
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 8px;
}

.service-item:hover {
  background: rgba(99, 102, 241, 0.05);
}

.service-item.active {
  background: rgba(99, 102, 241, 0.15);
  color: var(--primary);
  border-left-color: var(--primary);
  font-weight: 500;
}

.service-name {
  flex: 1;
}

.service-actions {
  position: relative;
  display: flex;
  align-items: center;
  flex-shrink: 0;
}

.btn-more-service {
  width: 20px;
  height: 20px;
  padding: 0;
  background: transparent;
  color: var(--text-secondary);
  border: none;
  border-radius: 4px;
  font-size: 14px;
  display: flex;
  align-items: center;
  justify-content: center;
  opacity: 0;
  transition: opacity 0.2s;
  cursor: pointer;
  line-height: 1;
}

.service-item:hover .btn-more-service {
  opacity: 1;
}

.btn-more-service:hover {
  background: var(--bg-light);
  color: var(--text-primary);
  opacity: 1;
}

.service-add-item {
  padding: 10px 20px 10px 48px;
  cursor: pointer;
  transition: all 0.2s;
  border-left: 3px solid transparent;
  font-size: 14px;
  display: flex;
  align-items: center;
  gap: 8px;
  color: var(--text-secondary);
}

.service-add-item:hover {
  background: rgba(99, 102, 241, 0.05);
  color: var(--primary);
}

.service-add-icon {
  font-size: 18px;
  font-weight: 600;
}

.service-add-text {
  font-size: 14px;
}

.domain-actions {
  position: relative;
  display: flex;
  align-items: center;
  flex-shrink: 0;
}

.btn-more {
  width: 24px;
  height: 24px;
  padding: 0;
  background: transparent;
  color: var(--text-secondary);
  border: none;
  border-radius: 4px;
  font-size: 16px;
  display: flex;
  align-items: center;
  justify-content: center;
  opacity: 0;
  transition: opacity 0.2s;
  cursor: pointer;
  line-height: 1;
}

.domain-item:hover .btn-more {
  opacity: 1;
}

.btn-more:hover {
  background: var(--bg-light);
  color: var(--text-primary);
  opacity: 1;
}

.context-menu {
  position: absolute;
  top: 100%;
  right: 0;
  margin-top: 4px;
  background: white;
  border: 1px solid var(--border);
  border-radius: 6px;
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.15);
  z-index: 1000;
  min-width: 120px;
  overflow: hidden;
}

.menu-item {
  display: block;
  width: 100%;
  padding: 10px 16px;
  background: none;
  border: none;
  text-align: left;
  font-size: 14px;
  color: var(--text-primary);
  cursor: pointer;
  transition: background 0.2s;
}

.menu-item:hover {
  background: var(--bg-light);
}

.menu-item-danger {
  color: var(--danger);
}

.menu-item-danger:hover {
  background: #fee2e2;
}
</style>

