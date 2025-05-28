<script setup>
import { computed, useAttrs, defineProps } from "vue";
import { useRouter } from "vue-router";
import { tabs } from "@/assets/data/tabs";

const props = defineProps({
  category: {
    type: String,
    default: ""
  },
  type: {
    type: String,
    default: "button"
  },
  size: {
    type: String,
    default: "md"
  },
  isActive: {
    type: Boolean,
    default: false
  },
  showEmoji: {
    type: Boolean,
    default: false
  }
});

const type = computed(() => props.type);
const size = computed(() => props.size);
const isActive = computed(() => props.isActive);

// 카테고리에 맞는 이모지 찾기
const categoryEmoji = computed(() => {
  if (!props.showEmoji || !props.category) return "";
  const tab = tabs.find(tab => tab.value === props.category);
  return tab ? tab.emoji + " " : "";
});

const router = useRouter();

const buttonSizeClass = computed(() => size.value);
const buttonTypeClass = computed(() => type.value);

const attrs = useAttrs();

function handleClick() {
  if (props.to) {
    router.push(props.to);
  }
}
</script>

<template>
  <button
    :class="[
      'toggle-button',
      props.class,
      buttonSizeClass,
      buttonTypeClass,
      { active: isActive },
    ]"
    v-bind="attrs"
    @click="handleClick"
  >
    <span v-if="showEmoji && categoryEmoji">{{ categoryEmoji }}</span>
    <slot></slot>
  </button>
</template>

<style scoped lang="scss">
.toggle-button {
  white-space: nowrap;
  padding: 10px 20px;
  font-size: 16px;
  border: 1px solid #ccc;
  border-radius: 8px;
  background-color: white;
  color: var(--c-text);
  text-align: center;
  cursor: pointer;

  &.tag {
    background-color: #f5f5f5;
    cursor: default;
    border: none;
    font-weight: 600;
  }

  &.active {
    background-color: #000;
    color: #fff;

    &:hover {
      background-color: rgba(0, 0, 0, 0.8);
    }
  }

  &:hover {
    background-color: rgba(236, 236, 236, 0.5);
  }

  &.sm {
    padding: 4px 10px;
    font-size: 12px;
  }

  &.md {
    padding: 8px 12px;
    font-size: 14px;
  }

  &:disabled {
    pointer-events: none;
  }
}
</style>
