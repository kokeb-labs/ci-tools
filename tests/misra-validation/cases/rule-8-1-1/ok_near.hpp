// Near misses: compliant code close to a violation.
#ifndef KV_RULE_8_1_1_OK_NEAR_HPP
#define KV_RULE_8_1_1_OK_NEAR_HPP

#include <cstdint>

namespace kv::rule_8_1_1::ok_near {

class Gauge {
 public:
  std::uint32_t peek() {
    return [&]() -> std::uint32_t { return level_; }();
  }

  std::uint32_t named_this() {
    auto f = [this]() -> std::uint32_t { return level_; };
    return f();
  }

  std::uint32_t no_member(std::uint32_t v) {
    auto g = [v]() -> std::uint32_t { return v; };
    return g();
  }

 private:
  std::uint32_t level_{0U};
};

}  // namespace kv::rule_8_1_1::ok_near

#endif  // KV_RULE_8_1_1_OK_NEAR_HPP
