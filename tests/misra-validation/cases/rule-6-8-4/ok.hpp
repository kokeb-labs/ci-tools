#ifndef KV_RULE_6_8_4_OK_HPP
#define KV_RULE_6_8_4_OK_HPP

// Compliant: the members are lvalue-ref-qualified, so a temporary cannot hand out a reference.
#include <cstdint>

namespace kv::rule_6_8_4::ok {

class Buffer {
 public:
  std::int32_t const& first() const& { return data_; }
  std::int32_t const& first() const&& = delete;
  Buffer& self() & { return *this; }

 private:
  std::int32_t data_{0};
};

}  // namespace kv::rule_6_8_4::ok

#endif  // KV_RULE_6_8_4_OK_HPP
