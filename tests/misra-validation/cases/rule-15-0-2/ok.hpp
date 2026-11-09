#ifndef KV_RULE_15_0_2_OK_HPP
#define KV_RULE_15_0_2_OK_HPP

// Compliant: the copy and move members have the conventional, ref-qualified signatures.
#include <cstdint>

namespace kv::rule_15_0_2::ok {

class Counter {
 public:
  Counter() = default;
  Counter(const Counter&) = default;
  Counter(Counter&&) noexcept = default;
  Counter& operator=(const Counter&) & = default;
  Counter& operator=(Counter&&) & noexcept = default;
  ~Counter() = default;

  [[nodiscard]] std::uint32_t count() const { return count_; }

 private:
  std::uint32_t count_ = 0U;
};

}  // namespace kv::rule_15_0_2::ok

#endif  // KV_RULE_15_0_2_OK_HPP
