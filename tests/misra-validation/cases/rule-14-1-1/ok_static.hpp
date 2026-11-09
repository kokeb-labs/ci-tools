// Near miss: a public static constant beside private data.
#ifndef KV_RULE_14_1_1_OK_STATIC_HPP
#define KV_RULE_14_1_1_OK_STATIC_HPP

#include <cstdint>

namespace kv::rule_14_1_1::ok_static {

class Gain {
 public:
  static constexpr std::int32_t kMax = 64;

  [[nodiscard]] std::int32_t value() const { return value_; }

 private:
  std::int32_t value_ = 1;
};

}  // namespace kv::rule_14_1_1::ok_static

#endif  // KV_RULE_14_1_1_OK_STATIC_HPP
