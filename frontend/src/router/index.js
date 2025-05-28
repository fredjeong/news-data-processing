import NotFoundView from "@/views/NotFoundView.vue";
import { createRouter, createWebHistory } from "vue-router";
import NewsView from "@/views/NewsView.vue";
import NewsDetailView from "@/views/NewsDetailView.vue";
import DashBoardView from "@/views/DashBoardView.vue";
import LoginView from "@/views/LoginView.vue";
import RegisterView from "@/views/RegisterView.vue";
import SearchResultView from "@/views/SearchResultView.vue";
import MyPageView from "@/views/MyPageView.vue";

const router = createRouter({
  history: createWebHistory("/"),
  routes: [
    {
      path: "/",
      redirect: "/news",
    },
    {
      path: "/login",
      name: "login",
      component: LoginView,
      meta: { requiresAuth: false },
    },
    {
      path: "/register",
      name: "register",
      component: RegisterView,
      meta: { requiresAuth: false },
    },
    {
      path: "/news",
      name: "News",
      component: NewsView,
      meta: { requiresAuth: false },
    },
    {
      path: "/news/:id",
      name: "newsDetail",
      component: NewsDetailView,
      props: true,
      meta: { requiresAuth: true },
    },
    {
      path: "/dashboard",
      name: "dashboard",
      component: DashBoardView,
      meta: { requiresAuth: true },
    },
    {
      path: "/mypage",
      name: "mypage",
      component: MyPageView,
      meta: { requiresAuth: true },
    },
    {
      path: "/search",
      name: "search",
      component: SearchResultView,
      meta: { requiresAuth: false },
    },
    {
      path: "/:pathMatch(.*)*",
      component: NotFoundView,
    },
  ],
});

// 네비게이션 가드 활성화
router.beforeEach((to, from, next) => {
  const isAuthenticated = localStorage.getItem('access_token');
  
  if (to.meta.requiresAuth && !isAuthenticated) {
    // 인증이 필요한 페이지에 접근하려고 할 때 로그인 페이지로 리다이렉트
    next('/login');
  } else if ((to.path === '/login' || to.path === '/register') && isAuthenticated) {
    // 이미 로그인한 사용자가 로그인 페이지에 접근하려고 할 때 메인 페이지로 리다이렉트
    next('/');
  } else {
    next();
  }
});

export default router;