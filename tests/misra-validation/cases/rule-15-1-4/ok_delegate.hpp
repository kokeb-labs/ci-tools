// Near miss: the default constructor delegates, so every member is set.
#ifndef KV_RULE_15_1_4_OK_DELEGATE_HPP
#define KV_RULE_15_1_4_OK_DELEGATE_HPP

#include <cstdint>

namespace kv::rule_15_1_4::ok_delegate {

class Timer {
 public:
  explicit Timer(std::uint32_t period) : period_(period), count_(0U) {}
  Timer() : Timer(10U) {}

  [[nodiscard]] std::uint32_t period() const { return period_; }
  [[nodiscard]] std::uint32_t count() const { return count_; }

 private:
  std::uint32_t period_;
  std::uint32_t count_;
};

}  // namespace kv::rule_15_1_4::ok_delegate

#endif  // KV_RULE_15_1_4_OK_DELEGATE_HPP
