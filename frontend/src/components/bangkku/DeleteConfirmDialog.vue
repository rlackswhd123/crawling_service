<script setup lang="ts">
import {
  Dialog,
  DialogContent,
  DialogDescription,
  DialogFooter,
  DialogHeader,
  DialogTitle,
} from '@/components/ui/dialog';
import { Button } from '@/components/ui/button';

interface Props {
  open: boolean;
  promptText: string;
}

const props = defineProps<Props>();

const emit = defineEmits<{
  'update:open': [value: boolean];
  'confirm': [];
}>();

const handleClose = () => {
  emit('update:open', false);
};

const handleConfirm = () => {
  emit('confirm');
  handleClose();
};
</script>

<template>
  <Dialog :open="open" @update:open="handleClose">
    <DialogContent class="sm:max-w-md">
      <DialogHeader>
        <DialogTitle>프롬프트 삭제</DialogTitle>
        <DialogDescription>
          이 프롬프트를 정말 삭제하시겠습니까?
        </DialogDescription>
      </DialogHeader>

      <div class="py-4">
        <div class="p-3 bg-gray-50 rounded-lg border border-gray-200">
          <p class="text-sm text-gray-700 line-clamp-3">
            {{ promptText }}
          </p>
        </div>

        <p class="text-sm text-red-600 mt-4">
          ⚠️ 삭제된 프롬프트는 복구할 수 없습니다.
        </p>
      </div>

      <DialogFooter>
        <Button variant="outline" @click="handleClose">
          취소
        </Button>
        <Button variant="destructive" @click="handleConfirm">
          삭제
        </Button>
      </DialogFooter>
    </DialogContent>
  </Dialog>
</template>
