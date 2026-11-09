// Near misses: compliant code that resembles a violation.
#ifndef KV_RULE_6_8_4_OK_NEAR_HPP
#define KV_RULE_6_8_4_OK_NEAR_HPP

#include <cstdint>

namespace kv::rule_6_8_4::near {

class Table {
 public:
  // Returns by value: nothing can dangle, no ref-qualifier is needed.
  [[nodiscard]] std::int32_t value() const { return cells_; }
  // Pointer into *this, ref-qualified, with the rvalue form deleted.
  [[nodiscard]] const std::int32_t* data() const& { return &cells_; }
  const std::int32_t* data() const&& = delete;

 private:
  std::int32_t cells_{0};
};

}  // namespace kv::rule_6_8_4::near

#endif  // KV_RULE_6_8_4_OK_NEAR_HPP
