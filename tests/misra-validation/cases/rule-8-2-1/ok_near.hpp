// Near misses: compliant code close to a violation.
#ifndef KV_RULE_8_2_1_OK_NEAR_HPP
#define KV_RULE_8_2_1_OK_NEAR_HPP

#include <cstdint>

namespace kv::rule_8_2_1::ok_near {

struct Base {
  std::int32_t id{0};
};

struct Middle : Base {
  std::int32_t level{0};
};

struct Derived : Middle {
  std::int32_t extra{0};
};

inline std::int32_t down(Base const& b) { return static_cast<Derived const&>(b).extra; }

inline std::int32_t level_of(Base const& b) { return static_cast<Middle const&>(b).level; }

inline std::int32_t up(Derived const& d) {
  Base const& b = d;
  return b.id;
}

}  // namespace kv::rule_8_2_1::ok_near

#endif  // KV_RULE_8_2_1_OK_NEAR_HPP
