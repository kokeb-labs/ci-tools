#ifndef KV_RULE_15_0_1_OK_HPP
#define KV_RULE_15_0_1_OK_HPP

// Compliant: every special member is declared, all defaulted, so the class is plainly copyable.
#include <cstdint>

namespace kv::rule_15_0_1::ok {

class Buffer {
 public:
  Buffer() = default;
  Buffer(const Buffer&) = default;
  Buffer(Buffer&&) noexcept = default;
  Buffer& operator=(const Buffer&) = default;
  Buffer& operator=(Buffer&&) noexcept = default;
  ~Buffer() = default;

  [[nodiscard]] std::uint32_t size() const { return size_; }

 private:
  std::uint32_t size_ = 0U;
};

class Handle {
 public:
  Handle() = default;
  Handle(const Handle&) = delete;
  Handle(Handle&&) = delete;
  Handle& operator=(const Handle&) = delete;
  Handle& operator=(Handle&&) = delete;
  ~Handle() = default;

  [[nodiscard]] std::uint32_t id() const { return id_; }

 private:
  std::uint32_t id_ = 0U;
};

}  // namespace kv::rule_15_0_1::ok

#endif  // KV_RULE_15_0_1_OK_HPP
