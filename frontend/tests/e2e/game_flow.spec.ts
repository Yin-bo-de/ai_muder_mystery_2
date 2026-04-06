/**
 * 端到端UI测试 - 完整游戏流程
 * 使用Playwright测试框架
 * 运行命令：npx playwright test
 */
import { test, expect } from '@playwright/test'

test.describe('AI侦探社完整游戏流程测试', () => {
  test.beforeEach(async ({ page }) => {
    // 访问首页
    await page.goto('http://localhost:5173')
  })

  test('首页加载正常', async ({ page }) => {
    // 验证页面标题
    await expect(page).toHaveTitle(/AI侦探社/)

    // 验证"开始新案件"按钮存在
    const startButton = page.getByRole('button', { name: '开始新案件' })
    await expect(startButton).toBeVisible()
    await expect(startButton).toBeEnabled()

    // 验证其他功能按钮存在
    await expect(page.getByRole('button', { name: '案件记录' })).toBeVisible()
    await expect(page.getByRole('button', { name: '成就系统' })).toBeVisible()
  })

  test('案件创建流程正常', async ({ page }) => {
    // 点击开始新案件
    await page.getByRole('button', { name: '开始新案件' }).click()

    // 验证跳转到案件生成页面
    await expect(page).toHaveURL('/game')

    // 验证加载状态显示
    await expect(page.getByText('案件生成中...')).toBeVisible()
    await expect(page.getByRole('progressbar')).toBeVisible()
  })

  test.describe('游戏内页面导航测试', () => {
    test.beforeEach(async ({ page }) => {
      // 模拟已进入游戏，直接访问勘查页面
      await page.goto('http://localhost:5173/investigation')
    })

    test('侧边栏导航正常', async ({ page }) => {
      // 验证侧边栏菜单存在
      await expect(page.getByRole('link', { name: '现场勘查' })).toBeVisible()
      await expect(page.getByRole('link', { name: '质询嫌疑人' })).toBeVisible()
      await expect(page.getByRole('link', { name: '线索库' })).toBeVisible()
      await expect(page.getByRole('link', { name: '指认凶手' })).toBeVisible()
      await expect(page.getByRole('link', { name: '结案报告' })).toBeVisible()

      // 测试导航到质询页面
      await page.getByRole('link', { name: '质询嫌疑人' }).click()
      await expect(page).toHaveURL('/interrogation')
      await expect(page.getByText('质询嫌疑人')).toBeVisible()

      // 测试导航到线索库页面
      await page.getByRole('link', { name: '线索库' }).click()
      await expect(page).toHaveURL('/clues')
      await expect(page.getByText('线索库')).toBeVisible()

      // 测试导航到指认页面
      await page.getByRole('link', { name: '指认凶手' }).click()
      await expect(page).toHaveURL('/accuse')
      await expect(page.getByText('指认凶手')).toBeVisible()
    })

    test('顶部功能区正常', async ({ page }) => {
      // 验证计时器存在
      await expect(page.getByText(/^\d{2}:\d{2}$/)).toBeVisible()

      // 验证线索进度条存在
      await expect(page.getByRole('progressbar', { name: /线索/ })).toBeVisible()

      // 验证线索库快捷按钮存在
      const clueButton = page.getByRole('button', { name: '线索库' })
      await expect(clueButton).toBeVisible()

      // 点击线索库按钮跳转
      await clueButton.click()
      await expect(page).toHaveURL('/clues')
    })

    test('返回首页功能正常', async ({ page }) => {
      // 点击首页按钮
      await page.getByRole('button', { name: '回到主页' }).click()
      await expect(page).toHaveURL('/')
      await expect(page.getByRole('button', { name: '开始新案件' })).toBeVisible()
    })
  })

  test.describe('现场勘查页面功能', () => {
    test.beforeEach(async ({ page }) => {
      await page.goto('http://localhost:5173/investigation')
    })

    test('页面元素加载正常', async ({ page }) => {
      await expect(page.getByText('现场勘查')).toBeVisible()
      await expect(page.getByText('案发现场信息')).toBeVisible()
      await expect(page.getByText('可勘查区域')).toBeVisible()

      // 验证场景卡片存在
      const sceneCards = page.getByRole('img', { name: /勘查/ })
      await expect(sceneCards.first()).toBeVisible()
    })

    test('勘查功能正常', async ({ page }) => {
      // 点击第一个场景的勘查按钮
      const firstScene = page.getByRole('button', { name: '勘查' }).first()
      await firstScene.click()

      // 验证勘查结果提示出现
      await expect(page.getByRole('alert')).toBeVisible()
    })
  })

  test.describe('质询页面功能', () => {
    test.beforeEach(async ({ page }) => {
      await page.goto('http://localhost:5173/interrogation')
    })

    test('页面元素加载正常', async ({ page }) => {
      await expect(page.getByText('质询嫌疑人')).toBeVisible()

      // 验证嫌疑人头像存在
      const avatars = page.locator('.ant-avatar')
      await expect(avatars.first()).toBeVisible()

      // 验证模式切换按钮存在
      await expect(page.getByRole('radio', { name: '全体质询' })).toBeVisible()
      await expect(page.getByRole('radio', { name: '单独审讯' })).toBeVisible()

      // 验证消息输入框存在
      await expect(page.getByPlaceholder(/对所有嫌疑人说点什么/)).toBeVisible()
      await expect(page.getByRole('button', { name: '发送' })).toBeVisible()
    })

    test('消息发送功能正常', async ({ page }) => {
      // 输入测试消息
      const input = page.getByPlaceholder(/对所有嫌疑人说点什么/)
      await input.fill('你们好，我是负责这个案件的侦探')

      // 点击发送
      await page.getByRole('button', { name: '发送' }).click()

      // 验证消息出现在对话中
      await expect(page.getByText('你们好，我是负责这个案件的侦探')).toBeVisible()
    })
  })

  test.describe('线索库页面功能', () => {
    test.beforeEach(async ({ page }) => {
      await page.goto('http://localhost:5173/clues')
    })

    test('页面元素加载正常', async ({ page }) => {
      await expect(page.getByText('线索库')).toBeVisible()

      // 验证统计卡片存在
      await expect(page.getByText('线索收集率')).toBeVisible()
      await expect(page.getByText('物证')).toBeVisible()
      await expect(page.getByText('证词')).toBeVisible()

      // 验证标签页存在
      await expect(page.getByRole('tab', { name: '全部线索' })).toBeVisible()
      await expect(page.getByRole('tab', { name: '物证' })).toBeVisible()
      await expect(page.getByRole('tab', { name: '证词' })).toBeVisible()

      // 验证关联线索按钮存在
      await expect(page.getByRole('button', { name: '关联线索' })).toBeVisible()
    })

    test('线索筛选功能正常', async ({ page }) => {
      // 点击物证标签
      await page.getByRole('tab', { name: '物证' }).click()
      await expect(page.getByRole('tab', { name: '物证' })).toHaveAttribute('aria-selected', 'true')

      // 点击证词标签
      await page.getByRole('tab', { name: '证词' }).click()
      await expect(page.getByRole('tab', { name: '证词' })).toHaveAttribute('aria-selected', 'true')
    })
  })

  test.describe('指认页面功能', () => {
    test.beforeEach(async ({ page }) => {
      await page.goto('http://localhost:5173/accuse')
    })

    test('页面元素加载正常', async ({ page }) => {
      await expect(page.getByText('指认凶手')).toBeVisible()

      // 验证步骤指示器存在
      await expect(page.getByText('选择嫌疑人')).toBeVisible()
      await expect(page.getByText('陈述推理')).toBeVisible()
      await expect(page.getByText('提交证据')).toBeVisible()
      await expect(page.getByText('确认提交')).toBeVisible()

      // 验证剩余次数提示存在
      await expect(page.getByText(/剩余指认机会/)).toBeVisible()
    })

    test('多步骤指认流程正常', async ({ page }) => {
      // 第一步：选择嫌疑人
      const firstSuspect = page.getByRole('img', { name: /嫌疑人/ }).first()
      await firstSuspect.click()
      await page.getByRole('button', { name: '下一步' }).click()

      // 第二步：填写动机和作案手法
      await page.getByPlaceholder(/请详细描述你推理的作案动机/).fill('因为死者欠他钱不还')
      await page.getByPlaceholder(/请详细描述作案过程/).fill('他用水果刀刺死了死者')
      await page.getByRole('button', { name: '下一步' }).click()

      // 第三步：选择证据
      await page.getByRole('button', { name: '下一步' }).click()

      // 第四步：确认提交
      await expect(page.getByText('确认你的指认信息')).toBeVisible()
      await expect(page.getByRole('button', { name: '提交指认' })).toBeVisible()
    })
  })
})
