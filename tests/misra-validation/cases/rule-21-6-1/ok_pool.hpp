// Compliant near miss: a fixed pool with an allocate member that hands out its own static slots.
#ifndef KV_RULE_21_6_1_OK_POOL_HPP
#define KV_RULE_21_6_1_OK_POOL_HPP

#include <array>
#include <cstddef>
#include <cstdint>

namespace kv::rule_21_6_1::ok_pool {

class Pool {
 public:
  [[nodiscard]] std::int32_t* allocate() {
    if (used_ >= slots_.size()) {
      return nullptr;
    }
    std::int32_t* slot = &slots_[used_];
    ++used_;
    return slot;
  }

 private:
  std::array<std::int32_t, 4U> slots_{};
  std::size_t used_{0U};
};

}  // namespace kv::rule_21_6_1::ok_pool

#endif  // KV_RULE_21_6_1_OK_POOL_HPP
