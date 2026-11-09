// Near miss: assignment from a raw value is not a copy or move member.
#ifndef KV_RULE_15_0_2_OK_OTHER_HPP
#define KV_RULE_15_0_2_OK_OTHER_HPP

#include <cstdint>

namespace kv::rule_15_0_2::ok_other {

class Counter {
 public:
  Counter() = default;
  Counter& operator=(std::uint32_t value) & {
    count_ = value;
    return *this;
  }

  [[nodiscard]] std::uint32_t count() const { return count_; }

 private:
  std::uint32_t count_ = 0U;
};

}  // namespace kv::rule_15_0_2::ok_other

#endif  // KV_RULE_15_0_2_OK_OTHER_HPP
