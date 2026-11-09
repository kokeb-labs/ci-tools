// Seeded violation: a function pointer is cast to an object pointer.
namespace kv::rule_8_2_4::bad {

int handler(int code) {
  return code;
}

void* as_object() {
  return reinterpret_cast<void*>(&handler);
}

}  // namespace kv::rule_8_2_4::bad
