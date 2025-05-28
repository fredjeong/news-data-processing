<script setup>
import { useDate } from "@/composables/useDate";
import { defineProps } from "vue";

const props = defineProps();

const { formatDate } = useDate();
</script>

<template>
  <article class="comment">
    <div class="comment__header">
      <span class="comment__header-author">{{ props.writer_name }}</span>
      <span class="comment__header-date">{{
        formatDate(props.write_date)
      }}</span>
    </div>
    <p class="comment__content">{{ props.content }}</p>
  </article>
</template>

<style scoped lang="scss">
.comment {
  padding: 10px;
  background-color: #f6f6f6;
  margin: 10px 0;
  border-radius: 10px;
  display: flex;
  flex-direction: column;
  gap: 7px;

  &__header {
    display: flex;
    gap: 10px;
    font-size: 0.9rem;
    color: #666;
    margin-bottom: 5px;
    &-author {
      font-weight: bold;
    }
    &-date {
      color: #999;
      font-size: 0.8rem;
    }
  }
  &__content {
    font-size: 1rem;
    line-height: 1.4;
  }
}
</style>
