<script setup lang="ts">
import { computed } from 'vue';
import { useRoute } from 'vue-router';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card';

const route = useRoute();

const serviceTitle = computed(() => {
	const service = route.meta.service as string;
	if (service === 'anytalk') return '애니톡';
	if (service === 'baik') return 'BAIK';
	return 'Coming Soon';
});
</script>


<template>
  <div class="flex items-center justify-center h-full bg-gray-50">
    <Card class="w-full max-w-md">
      <CardHeader>
        <CardTitle class="text-2xl text-center">{{ serviceTitle }}</CardTitle>
        <CardDescription class="text-center">
          서비스 준비 중입니다
        </CardDescription>
      </CardHeader>
      <CardContent class="text-center space-y-4">
        <div class="text-6xl">🚧</div>
        <p class="text-gray-600">
          {{ serviceTitle }} 서비스는 현재 개발 중입니다.<br />
          조금만 기다려 주세요!
        </p>
      </CardContent>
    </Card>
  </div>
</template>

