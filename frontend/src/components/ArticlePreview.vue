<script setup>
import ContentBox from "@/common/ContentBox.vue";
import StateButton from "@/common/StateButton.vue";
import { useDate } from "@/composables/useDate";
import { defineProps, computed } from "vue";
import { RouterLink } from "vue-router";
import { tabs } from "@/assets/data/tabs";

const props = defineProps({
  news: {
    type: Object,
    required: true,
  },
  to: {
    type: String,
    default: null,
  },
});

const { formatDate } = useDate();
const linkComponent = computed(() => (props.to ? RouterLink : "div"));

// RouterLink props 계산
const linkProps = computed(() => {
  if (props.to) {
    return { to: props.to };
  }
  return {};
});


// 카테고리에 맞는 이모지 찾기
const categoryEmoji = computed(() => {
  const category = props.news.category;
  const tab = tabs.find(tab => tab.value === category);
  return tab ? tab.emoji : "🏷️"; // 매칭되는 카테고리가 없을 경우 기본 이모지 사용
});
</script>

<template>
  <component :is="linkComponent" v-bind="linkProps" class="article-preview-link">
    <ContentBox>
      <div class="category">
        {{ categoryEmoji }} {{ props.news.category }}
      </div>
      <div class="top">
        <h1>{{ props.news.title }}</h1>
      </div>
      <div class="bottom"> 
        <div class="bottom__date">
          {{ formatDate(new Date(props.news.write_date)) }}
        </div>
        <div class="bottom__icons">
          <div>
            ❤️ {{ props.news.like_count }}
          </div>
          <div>
            👀 {{ props.news.view_count }}
          </div>
        </div>
      </div>
    </ContentBox>
  </component>
</template>

<style scoped lang="scss">
.article-preview-link {
  display: block;
  text-decoration: none;
  color: inherit;
  transition: all 0.3s ease;
  
  &:hover {
    transform: translateY(-2px);
    
    .top h1 {
      color: #667eea;
    }
  }
  
  // RouterLink일 때 커서 포인터 표시
  &[href] {
    cursor: pointer;
  }
}

.category {
  font-size: 14px;
  margin-bottom: 8px;
  color: #666;
}

.top {
  h1 {
    font-size: 15px;
    transition: color 0.3s ease;
  }
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 5px;
}

.bottom {
  display: flex;
  align-items: baseline;
  gap: 10px;
  justify-content: space-between;

  &__date {
    font-size: 13px;
    color: #777;
  }

  &__icons {
    display: flex;
    gap: 10px;
  }
}
</style>
