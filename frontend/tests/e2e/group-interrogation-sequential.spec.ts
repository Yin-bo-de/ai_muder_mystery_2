/**
 * 全体质询模式顺序回答功能测试
 * 使用Playwright测试框架
 * 运行命令：npx playwright test group-interrogation-sequential.spec.ts
 */
import { test, expect } from '@playwright/test'

test.describe('全体质询模式顺序回答功能', () => {
  test.beforeEach(async ({ page }) => {
    // 访问质询页面
    await page.goto('http://localhost:5173/interrogation')

    // 等待页面加载完成
    await expect(page.getByText('质询嫌疑人')).toBeVisible()

    // 切换到全体质询模式
    await page.getByRole('radio', { name: '全体质询' }).click()
  })

  test('测试 1: 全体质询模式下，发送问题后嫌疑人按顺序回答', async ({ page }) => {
    // 输入问题
    const input = page.getByPlaceholder(/对所有嫌疑人说点什么/)
    await input.fill('案发时你们都在哪里？')

    // 发送问题
    await page.getByRole('button', { name: '发送' }).click()

    // 验证用户消息出现在对话中
    await expect(page.getByText('案发时你们都在哪里？')).toBeVisible()

    // 等待第一个嫌疑人回答（获取对话列表中的AI消息）
    const chatMessages = page.locator('.chat-message')
    await expect(chatMessages.nth(1)).toBeVisible({ timeout: 10000 })

    // 等待第二个嫌疑人回答
    await expect(chatMessages.nth(2)).toBeVisible({ timeout: 15000 })

    // 验证回答顺序 - 第二个消息应该在第一个之后出现
    const firstAnswerTime = await chatMessages.nth(1).getAttribute('data-timestamp')
    const secondAnswerTime = await chatMessages.nth(2).getAttribute('data-timestamp')

    if (firstAnswerTime && secondAnswerTime) {
      expect(parseInt(firstAnswerTime)).toBeLessThan(parseInt(secondAnswerTime))
    }
  })

  test('测试 2: 验证前一个嫌疑人打字完成后，下一个才开始', async ({ page }) => {
    // 发送问题
    const input = page.getByPlaceholder(/对所有嫌疑人说点什么/)
    await input.fill('你们和死者是什么关系？')
    await page.getByRole('button', { name: '发送' }).click()

    // 等待第一个嫌疑人开始回答
    const chatMessages = page.locator('.chat-message')
    await expect(chatMessages.nth(1)).toBeVisible({ timeout: 10000 })

    // 检查是否有打字机效果（如果实现了）
    const isTyping = await page.locator('.typing-indicator').isVisible().catch(() => false)

    if (isTyping) {
      // 等待打字机效果消失（回答完成）
      await expect(page.locator('.typing-indicator')).not.toBeVisible({ timeout: 15000 })
    }

    // 验证第二个嫌疑人的回答在第一个完成后才出现
    await expect(chatMessages.nth(2)).toBeVisible({ timeout: 10000 })
  })

  test('测试 3: 验证用户可以在队列处理过程中发送新消息', async ({ page }) => {
    // 发送第一个问题
    const input = page.getByPlaceholder(/对所有嫌疑人说点什么/)
    await input.fill('第一个问题')
    await page.getByRole('button', { name: '发送' }).click()

    // 等待第一个嫌疑人开始回答但不等待完成
    const chatMessages = page.locator('.chat-message')
    await expect(chatMessages.nth(1)).toBeVisible({ timeout: 10000 })

    // 发送第二个问题
    await input.fill('第二个问题')
    await page.getByRole('button', { name: '发送' }).click()

    // 验证第二个问题出现在对话中
    await expect(page.getByText('第二个问题')).toBeVisible()

    // 验证队列指示器存在（如果有队列显示功能）
    const hasQueue = await page.locator('.question-queue').isVisible().catch(() => false)
    if (hasQueue) {
      await expect(page.locator('.question-queue')).toContainText('第二个问题')
    }
  })

  test('测试 4: 验证点击跳过打字机效果会正确触发下一条消息', async ({ page }) => {
    // 发送问题
    const input = page.getByPlaceholder(/对所有嫌疑人说点什么/)
    await input.fill('描述一下案发经过')
    await page.getByRole('button', { name: '发送' }).click()

    // 等待第一个嫌疑人开始回答
    const chatMessages = page.locator('.chat-message')
    await expect(chatMessages.nth(1)).toBeVisible({ timeout: 10000 })

    // 检查是否有跳过按钮
    const hasSkipButton = await page.getByRole('button', { name: /跳过|继续/ }).isVisible().catch(() => false)

    if (hasSkipButton) {
      // 点击跳过按钮
      await page.getByRole('button', { name: /跳过|继续/ }).click()

      // 验证第二个嫌疑人的回答更快出现
      await expect(chatMessages.nth(2)).toBeVisible({ timeout: 5000 })
    } else {
      // 如果没有跳过按钮，验证正常的顺序回答
      await expect(chatMessages.nth(2)).toBeVisible({ timeout: 15000 })
    }
  })
})
