#ifndef KV_RULE_6_7_2_OK_HPP
#define KV_RULE_6_7_2_OK_HPP

// Compliant: namespace-scope objects are constexpr; mutable state lives in an object.
#include <cstdint>

namespace kv::rule_6_7_2::ok {

inline constexpr std::int32_t kMaxErrors{8};

class Stats {
 public:
  std::int32_t bump() {
    if (errors_ < kMaxErrors) {
      ++errors_;
    }
    return errors_;
  }

 private:
  std::int32_t errors_{0};
};

}  // namespace kv::rule_6_7_2::ok

#endif  // KV_RULE_6_7_2_OK_HPP
