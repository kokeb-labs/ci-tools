#ifndef KV_RULE_6_7_1_OK_HPP
#define KV_RULE_6_7_1_OK_HPP

// Compliant: the counter is owned by an object; a constant local may be static.
#include <cstdint>

namespace kv::rule_6_7_1::ok {

class IdSource {
 public:
  std::int32_t next() {
    static constexpr std::int32_t kStep{1};
    if (counter_ < kLimit) {
      counter_ += kStep;
    }
    return counter_;
  }

 private:
  static constexpr std::int32_t kLimit{1000};
  std::int32_t counter_{0};
};

}  // namespace kv::rule_6_7_1::ok

#endif  // KV_RULE_6_7_1_OK_HPP
