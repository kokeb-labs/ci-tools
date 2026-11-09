#ifndef KV_RULE_6_4_2_USING_OK_HPP
#define KV_RULE_6_4_2_USING_OK_HPP

// Compliant: the using-declaration brings in every base overload, and the derived overload has a new signature.
#include <cstdint>

namespace kv::rule_6_4_2_using::ok {

class Base {
 public:
  std::int32_t convert(std::int32_t v) const { return v; }
  std::int32_t convert(std::int16_t v) const { return static_cast<std::int32_t>(v); }
};

class Derived : public Base {
 public:
  using Base::convert;
  std::int32_t convert(std::int64_t v) const { return (v > 100) ? 100 : static_cast<std::int32_t>(v); }
};

inline std::int32_t use(Derived const& d) { return d.convert(std::int64_t{5}) + d.convert(std::int32_t{1}); }

}  // namespace kv::rule_6_4_2_using::ok

#endif  // KV_RULE_6_4_2_USING_OK_HPP
