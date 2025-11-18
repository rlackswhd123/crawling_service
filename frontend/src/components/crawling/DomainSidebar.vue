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
          <button
            class="btn-delete"
            @click.stop="$emit('delete-domain', domain.id)"
            title="도메인 삭제"
          >
            ×
          </button>
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
            <button
              class="btn-delete-service"
              @click.stop="$emit('delete-service', domain.id, service.id)"
              title="서비스 삭제"
            >
              ×
            </button>
          </div>
          <!-- 게시판 추가 버튼 -->
          <div 
            class="service-add-item"
            @click.stop="$emit('open-create-service-modal', domain.id)"
          >
            <span class="service-add-icon">+</span>
            <span class="service-add-text">게시판 추가</span>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref } from 'vue';
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
  'delete-domain': [domainId: number | string];
  'delete-service': [domainId: number | string, serviceId: number | string];
}>();

const expandedDomainId = ref<number | string | null>(null);

const toggleDomain = (domainId: number | string) => {
  if (expandedDomainId.value === domainId) {
    expandedDomainId.value = null;
  } else {
    expandedDomainId.value = domainId;
  }
};

const selectService = (domainId: number | string, serviceId: number | string) => {
  emit('select-service', domainId, serviceId);
};
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

.btn-delete-service {
  width: 20px;
  height: 20px;
  padding: 0;
  background: var(--danger);
  color: white;
  border-radius: 50%;
  font-size: 16px;
  display: flex;
  align-items: center;
  justify-content: center;
  opacity: 0;
  transition: opacity 0.2s;
  flex-shrink: 0;
}

.service-item:hover .btn-delete-service {
  opacity: 1;
}

.btn-delete-service:hover {
  background: #dc2626;
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

.btn-delete {
  width: 24px;
  height: 24px;
  padding: 0;
  background: var(--danger);
  color: white;
  border-radius: 50%;
  font-size: 18px;
  display: flex;
  align-items: center;
  justify-content: center;
  opacity: 0;
  transition: opacity 0.2s;
  flex-shrink: 0;
}

.domain-item:hover .btn-delete {
  opacity: 1;
}

.btn-delete:hover {
  background: #dc2626;
  opacity: 1;
}
</style>

